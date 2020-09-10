# microservices.py (m3-pyapi)
# Microservice classes

import json
import requests
from m3_pyapi.models import from_dict, CachedAncillaryDatum, CachedVideoReferenceInfo, ImageParams, Media, Observation, ImagedMoment, ImageReference, Association
from typing import Iterable, List


class AuthenticationError(Exception):
    """ Raised when authorization fails """
    def __init__(self, client_secret: str):
        super().__init__('Authentication error, check client secret: {}'.format(client_secret))


class AuthenticationMissingError(Exception):
    """ Raised when authentication is missing """
    def __init__(self):
        super().__init__('Authorization required')


class BadRequestError(Exception):
    """ Raised when a request is malformed """
    def __init__(self, message):
        super().__init__('Malformed request: {}'.format(message))


class NotFoundError(Exception):
    """ Raised when a resource is not found """
    def __init__(self, message):
        super().__init__('Not found: {}'.format(message))


class TimeoutError(Exception):
    """ Raised when the gateway times out """
    def __init__(self):
        super().__init__('Gateway timeout')


def handle_status(response: requests.Response):
    if response.status_code == 200:  # OK
        return
    elif response.status_code == 400:  # Malformed request
        raise BadRequestError(response.content.decode())
    elif response.status_code == 404:  # Resource not found
        raise NotFoundError(response.content.decode())
    elif response.status_code == 504:  # Gateway timeout
        raise TimeoutError()
    else:
        raise Exception(response)


class Microservice:
    """ Base microservice class """
    def __init__(self, base_url: str):
        self._base_url = base_url + ('/' if base_url[-1] != '/' else '')
        self._jwt = ''

    def url_to(self, endpoint: str) -> str:
        endpoint_parts = filter(bool, endpoint.split('/'))
        return self._base_url + '/'.join(endpoint_parts)

    def authenticate(self, client_secret: str):
        response = requests.post(self.url_to('auth'), headers = {
            'Authorization': 'APIKEY {}'.format(client_secret)
        })
        if response.status_code == 200:
            self._jwt = response.json()['access_token']
        else:
            raise AuthenticationError(client_secret)
    
    @property
    def authenticated(self) -> bool:
        return self._jwt != ''

    @property
    def _authorization_header(self) -> dict:
        if not self.authenticated:
            raise AuthenticationMissingError()
        return {'Authorization': 'BEARER {}'.format(self._jwt)}


class Annosaurus(Microservice):
    """ Annosaurus microservice """
    def __init__(self, base_url: str):
        super().__init__(base_url)
    
    # Ancillary Data ---
    def get_ancillary_data(self, uuid: str) -> CachedAncillaryDatum:
        response = requests.get(self.url_to('v1/ancillarydata/{}'.format(uuid)))
        handle_status(response)
        return from_dict(CachedAncillaryDatum, response.json())
    
    def get_ancillary_data_videoreference(self, uuid: str):
        response = requests.get(self.url_to('v1/ancillarydata/videoreference/{}'.format(uuid)))
        handle_status(response)
        return response.json()

    def get_ancillary_data_imagedmoment(self, uuid: str):
        response = requests.get(self.url_to('v1/ancillarydata/imagedmoment/{}'.format(uuid)))
        handle_status(response)
        return response.json()

    def get_ancillary_data_observation(self, uuid: str):
        response = requests.get(self.url_to('v1/ancillarydata/observation/{}'.format(uuid)))
        handle_status(response)
        return response.json()

    def create_ancillary_datum(self, ancillary_datum: CachedAncillaryDatum):
        response = requests.post(self.url_to('v1/ancillarydata'), headers=self._authorization_header, data=ancillary_datum.properties)
        handle_status(response)
        return response.json()
    
    def create_ancillary_data_bulk(self, ancillary_data: Iterable[CachedAncillaryDatum]):
        headers = self._authorization_header
        json_data = json.dumps([datum.properties for datum in ancillary_data])
        response = requests.post(self.url_to('v1/ancillarydata/bulk'), headers=headers, json=json_data)
        handle_status(response)
        return response.json()
    
    def merge_ancillary_data(self, uuid: str, ancillary_data: Iterable[CachedAncillaryDatum], window: int = 0):
        headers = self._authorization_header
        params = {'window': window} if window > 0 else None
        json_data = json.dumps([datum.properties for datum in ancillary_data])
        requests.put(self.url_to('v1/ancillarydata/merge/{}'.format(uuid)), headers=headers, params=params, json=json_data)
    # ---

    # Annotation (Observation) ---
    # TODO Annotation PUT, POST requests
    def get_annotation(self, uuid: str) -> Observation:
        response = requests.get(self.url_to('v1/annotations/{}'.format(uuid)))
        return from_dict(Observation, response.json())

    def get_annotations_videoreference(self, uuid: str, **params) -> List[Observation]:
        response = requests.get(self.url_to('v1/annotations/videoreference/{}'.format(uuid)), params=params)
        return [from_dict(Observation, obs_item) for obs_item in response.json()]
    
    def get_annotations_imagereference(self, uuid: str, **params) -> List[Observation]:
        response = requests.get(self.url_to('v1/annotations/imagereference/{}'.format(uuid)), params=params)
        return [from_dict(Observation, obs_item) for obs_item in response.json()]

    def get_annotations_videoreference_chunked(self, uuid: str, **params) -> List[Observation]:
        response = requests.get(self.url_to('v1/annotations/videoreference/chunked/{}'.format(uuid)), params=params)
        return [from_dict(Observation, obs_item) for obs_item in response.json()]
    # ---

    # Video Reference Info ---
    # TODO Video reference info PUT, POST, DELETE requests
    def get_vri_all(self, **params) -> List[CachedVideoReferenceInfo]:
        response = requests.get(self.url_to('v1/videoreferences/'), params=params)
        return [from_dict(CachedVideoReferenceInfo, vri_item) for vri_item in response.json()]
    
    def get_vri_uuid(self, uuid: str) -> CachedVideoReferenceInfo:
        response = requests.get(self.url_to('v1/videoreferences/{}'.format(uuid)))
        return from_dict(CachedVideoReferenceInfo, response.json())
    
    def get_videoreferenceuuid_all(self) -> dict:
        response = requests.get(self.url_to('v1/videoreferences/videoreferences'))
        return response.json()
    
    def get_vri_videoreferenceuuid(self, uuid: str) -> List[CachedVideoReferenceInfo]:
        response = requests.get(self.url_to('v1/videoreferences/videoreference/{}'.format(uuid)))
        return [from_dict(CachedVideoReferenceInfo, vri_item) for vri_item in response.json()]

    def get_missionids(self) -> dict:
        response = requests.get(self.url_to('v1/videoreferences/missionids'))
        return response.json()
    
    def get_vri_missionid(self, mission_id: str) -> List[CachedVideoReferenceInfo]:
        response = requests.get(self.url_to('v1/videoreferences/missionid/{}'.format(mission_id)))
        return [from_dict(CachedVideoReferenceInfo, vri_item) for vri_item in response.json()]

    def get_missioncontacts(self) -> dict:
        response = requests.get(self.url_to('v1/videoreferences/missioncontacts'))
        return response.json()
    
    def get_vri_missioncontact(self, mission_contact: str) -> List[CachedVideoReferenceInfo]:
        response = requests.get(self.url_to('v1/videoreferences/missioncontact/{}'.format(mission_contact)))
        return [from_dict(CachedVideoReferenceInfo, vri_item) for vri_item in response.json()]
    # ---


class Panoptes(Microservice):
    """ Panoptes microservice """
    def __init__(self, base_url: str):
        super().__init__(base_url)
    
    def upload_framegrab(self, image_file: str, camera_id: str, deployment_id: str, name: str):
        files = {'file': open(image_file, 'rb')}
        response = requests.post(self.url_to('v1/images/{}/{}/{}'.format(camera_id, deployment_id, name)), headers=self._authorization_header, files=files)
        handle_status(response)
        return ImageParams(response.json())

    def get_framegrab(self, camera_id: str, deployment_id: str, name: str):
        response = requests.get(self.url_to('v1/images/{}/{}/{}'.format(camera_id, deployment_id, name)))
        handle_status(response)
        return from_dict(ImageParams, response.json())

    def download_framegrab(self, image_file: str, camera_id: str, deployment_id: str, name: str):
        response = requests.get(self.url_to('v1/images/download/{}/{}/{}'.format(camera_id, deployment_id, name)))
        with open(image_file, 'wb') as f:
            f.write(response.content)


class VampireSquid(Microservice):
    """ Vampire Squid microservice """
    def __init__(self, base_url: str):
        super().__init__(base_url)

    def get_media_videoreference(self, uuid: str) -> Media:
        response = requests.get(self.url_to('v1/media/videoreference/{}'.format(uuid)))
        handle_status(response)
        return from_dict(Media, response.json())

    def get_media_videoreference_filename(self, filename: str) -> Media:
        response = requests.get(self.url_to('v1/media/videoreference/filename/{}'.format(filename)))
        handle_status(response)
        return from_dict(Media, response.json())

    def get_media_videosequence_name(self, name: str) -> List[Media]:
        response = requests.get(self.url_to('v1/media/videosequence/{}'.format(name)))
        handle_status(response)
        return [from_dict(Media, media_item) for media_item in response.json()]

    def get_media_video(self, name: str) -> List[Media]:
        response = requests.get(self.url_to('v1/media/video/{}'.format(name)))
        handle_status(response)
        return [from_dict(Media, media_item) for media_item in response.json()]

    def get_media_camera_timestamps(self, camera_id: str, start_time: str, end_time: str) -> List[Media]:
        response = requests.get(self.url_to('v1/media/camera/{}/{}/{}'.format(camera_id, start_time, end_time)))
        handle_status(response)
        return [from_dict(Media, media_item) for media_item in response.json()]

    def get_media_concurrent(self, uuid: str) -> List[Media]:
        response = requests.get(self.url_to('v1/media/concurrent/{}'.format(uuid)))
        handle_status(response)
        return [from_dict(Media, media_item) for media_item in response.json()]

    def get_media_camera_datetime(self, camera_id: str, date_time: str) -> List[Media]:
        # TODO Make this use python datetime objects
        response = requests.get(self.url_to('v1/media/camera/{}/{}'.format(camera_id, date_time)))
        handle_status(response)
        return [from_dict(Media, media_item) for media_item in response.json()]
    
    def get_media_uri(self, uri: str) -> Media:
        response = requests.get(self.url_to('v1/media/uri/{}'.format(uri)))
        handle_status(response)
        return from_dict(Media, response.json())



class KB(Microservice):
    pass


class Users(Microservice):
    pass
