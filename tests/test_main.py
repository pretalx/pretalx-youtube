import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django_scopes import scope

from pretalx_youtube.forms import YouTubeUrlForm
from pretalx_youtube.models import YouTubeLink
from pretalx_youtube.recording import YouTubeProvider

SETTINGS_URL_NAME = "plugins:pretalx_youtube:settings"


@pytest.mark.django_db
def test_orga_can_access_settings(orga_client, event):
    response = orga_client.get(
        reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug}),
        follow=True,
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_reviewer_cannot_access_settings(review_client, event):
    response = review_client.get(
        reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug}),
    )
    assert response.status_code == 404


# -- Model tests --


@pytest.mark.django_db
def test_youtube_link_properties(youtube_link):
    assert (
        youtube_link.player_link == "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ"
    )
    assert youtube_link.youtube_link == "https://youtube.com/watch?v=dQw4w9WgXcQ"
    assert "iframe" in youtube_link.iframe
    assert youtube_link.player_link in youtube_link.iframe


# -- Recording provider tests --


@pytest.mark.django_db
def test_recording_provider_with_link(event, confirmed_submission, youtube_link):
    provider = YouTubeProvider(event)
    result = provider.get_recording(confirmed_submission)
    assert result is not None
    assert "iframe" in result
    assert result["csp_header"] == "https://www.youtube-nocookie.com/"


@pytest.mark.django_db
def test_recording_provider_without_link(event, confirmed_submission):
    provider = YouTubeProvider(event)
    result = provider.get_recording(confirmed_submission)
    assert result is None


# -- Form tests --


@pytest.mark.django_db
def test_url_form_no_schedule(event):
    with scope(event=event):
        form = YouTubeUrlForm(event=event)
    assert len(form.fields) == 0


@pytest.mark.django_db
def test_url_form_with_schedule(event, slot):
    with scope(event=event):
        form = YouTubeUrlForm(event=event)
    assert len(form.fields) == 1


@pytest.mark.django_db
def test_url_form_with_existing_link(event, slot, youtube_link):
    with scope(event=event):
        form = YouTubeUrlForm(event=event)
    field = next(iter(form.fields.values()))
    assert field.initial == youtube_link.youtube_link


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("url", "expected_id"),
    (
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ),
)
def test_url_form_clean_valid(event, slot, url, expected_id):
    code = slot.submission.code
    with scope(event=event):
        form = YouTubeUrlForm(
            data={f"video_id_{code}": url},
            event=event,
        )
        assert form.is_valid(), form.errors
        assert form.cleaned_data[f"video_id_{code}"] == expected_id


@pytest.mark.django_db
def test_url_form_clean_invalid_url(event, slot):
    code = slot.submission.code
    with scope(event=event):
        form = YouTubeUrlForm(
            data={f"video_id_{code}": "https://example.com/video"},
            event=event,
        )
        assert not form.is_valid()


@pytest.mark.django_db
def test_url_form_clean_empty(event, slot):
    code = slot.submission.code
    with scope(event=event):
        form = YouTubeUrlForm(
            data={f"video_id_{code}": ""},
            event=event,
        )
        assert form.is_valid()
        assert form.cleaned_data[f"video_id_{code}"] is None


@pytest.mark.django_db
def test_url_form_save_creates_link(event, slot):
    code = slot.submission.code
    with scope(event=event):
        form = YouTubeUrlForm(
            data={f"video_id_{code}": "https://www.youtube.com/watch?v=abc123"},
            event=event,
        )
        assert form.is_valid()
        form.save()
    assert YouTubeLink.objects.filter(submission=slot.submission).exists()
    assert YouTubeLink.objects.get(submission=slot.submission).video_id == "abc123"


@pytest.mark.django_db
def test_url_form_save_deletes_link(event, slot, youtube_link):
    code = slot.submission.code
    with scope(event=event):
        form = YouTubeUrlForm(
            data={f"video_id_{code}": ""},
            event=event,
        )
        assert form.is_valid()
        form.save()
    assert not YouTubeLink.objects.filter(submission=slot.submission).exists()


# -- View tests --


@pytest.mark.django_db
def test_settings_shows_no_schedule_message(orga_client, event):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    response = orga_client.get(url, follow=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_post_no_schedule_shows_error(orga_client, event):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    response = orga_client.post(url, data={}, follow=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_post_manual_url(orga_client, event, slot):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    code = slot.submission.code
    response = orga_client.post(
        url,
        data={f"video_id_{code}": "https://www.youtube.com/watch?v=test123"},
        follow=True,
    )
    assert response.status_code == 200
    assert YouTubeLink.objects.filter(submission__code=code).exists()


@pytest.mark.django_db
def test_post_invalid_manual_url(orga_client, event, slot):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    code = slot.submission.code
    response = orga_client.post(
        url,
        data={f"video_id_{code}": "https://example.com/notaurl"},
        follow=True,
    )
    assert response.status_code == 200
    assert not YouTubeLink.objects.filter(submission__code=code).exists()


@pytest.mark.django_db
def test_upload_json_file(orga_client, event, slot):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    code = slot.submission.code
    data = json.dumps([{"submission": code, "video_id": "jsonvid1"}])
    upload = SimpleUploadedFile(
        "data.json", data.encode(), content_type="application/json"
    )
    response = orga_client.post(
        url,
        data={"action": "upload", "file": upload},
        follow=True,
    )
    assert response.status_code == 200
    assert YouTubeLink.objects.filter(
        submission__code=code, video_id="jsonvid1"
    ).exists()


@pytest.mark.django_db
def test_upload_csv_file(orga_client, event, slot):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    code = slot.submission.code
    csv_content = f"submission,video_id\n{code},csvvid1\n"
    upload = SimpleUploadedFile(
        "data.csv", csv_content.encode(), content_type="text/csv"
    )
    response = orga_client.post(
        url,
        data={"action": "upload", "file": upload},
        follow=True,
    )
    assert response.status_code == 200
    assert YouTubeLink.objects.filter(
        submission__code=code, video_id="csvvid1"
    ).exists()


@pytest.mark.django_db
def test_upload_invalid_file_type(orga_client, event, slot):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    upload = SimpleUploadedFile("data.txt", b"hello", content_type="text/plain")
    response = orga_client.post(
        url,
        data={"action": "upload", "file": upload},
        follow=True,
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_upload_no_file(orga_client, event, slot):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    response = orga_client.post(
        url,
        data={"action": "upload"},
        follow=True,
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_upload_invalid_json_content(orga_client, event, slot):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    data = json.dumps([{"submission": "NONEXIST", "video_id": "vid1"}])
    upload = SimpleUploadedFile(
        "data.json", data.encode(), content_type="application/json"
    )
    response = orga_client.post(
        url,
        data={"action": "upload", "file": upload},
        follow=True,
    )
    assert response.status_code == 200


# -- API tests --


@pytest.mark.django_db
def test_api_list(api_client, event, youtube_link):
    response = api_client.get(f"/api/events/{event.slug}/p/youtube/")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["results"][0]["video_id"] == "dQw4w9WgXcQ"
    assert (
        data["results"][0]["youtube_link"] == "https://youtube.com/watch?v=dQw4w9WgXcQ"
    )


@pytest.mark.django_db
def test_api_detail(api_client, event, youtube_link):
    code = youtube_link.submission.code
    response = api_client.get(f"/api/events/{event.slug}/p/youtube/{code}/")
    assert response.status_code == 200
    data = response.json()
    assert data["video_id"] == "dQw4w9WgXcQ"


@pytest.mark.django_db
def test_api_create(api_client, event, confirmed_submission):
    response = api_client.post(
        f"/api/events/{event.slug}/p/youtube/",
        data={"submission": confirmed_submission.code, "video_id": "newvid123"},
        format="json",
    )
    assert response.status_code == 201
    assert YouTubeLink.objects.filter(
        submission=confirmed_submission, video_id="newvid123"
    ).exists()


@pytest.mark.django_db
def test_api_update(api_client, event, youtube_link):
    code = youtube_link.submission.code
    response = api_client.patch(
        f"/api/events/{event.slug}/p/youtube/{code}/",
        data={"video_id": "updated123"},
        format="json",
    )
    assert response.status_code == 200
    youtube_link.refresh_from_db()
    assert youtube_link.video_id == "updated123"


@pytest.mark.django_db
def test_api_create_duplicate_updates(api_client, event, youtube_link):
    code = youtube_link.submission.code
    response = api_client.post(
        f"/api/events/{event.slug}/p/youtube/",
        data={"submission": code, "video_id": "replaced"},
        format="json",
    )
    assert response.status_code == 201
    assert YouTubeLink.objects.filter(submission__code=code).count() == 1
    assert YouTubeLink.objects.get(submission__code=code).video_id == "replaced"


@pytest.mark.django_db
def test_api_create_strips_url_from_video_id(api_client, event, confirmed_submission):
    response = api_client.post(
        f"/api/events/{event.slug}/p/youtube/",
        data={
            "submission": confirmed_submission.code,
            "video_id": "be/abc123",
        },
        format="json",
    )
    assert response.status_code == 201
    assert YouTubeLink.objects.get(submission=confirmed_submission).video_id == "abc123"


@pytest.mark.django_db
def test_api_bulk_import_json(api_client, event, confirmed_submission):
    data = [{"submission": confirmed_submission.code, "video_id": "bulkvid1"}]
    response = api_client.post(
        f"/api/events/{event.slug}/p/youtube/import/",
        data=data,
        format="json",
    )
    assert response.status_code == 201
    assert YouTubeLink.objects.filter(
        submission=confirmed_submission, video_id="bulkvid1"
    ).exists()


# -- Signal tests --


@pytest.mark.django_db
def test_nav_event_settings_signal(orga_client, event):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    response = orga_client.get(url, follow=True)
    assert response.status_code == 200
