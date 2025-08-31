from typing import Dict, Any, List


class SharedCamerasApiResponse:

    @classmethod
    def from_json(cls, data: List[Dict[str, Any]]) -> List[str]:
        if not data:
            return []
        return [SharedCamerasApiResponse.camera_id_from_json(d) for d in data[0].get('sharedCameras',[])]

    @classmethod
    def camera_id_from_json(cls, data: Dict[str, Any]) -> str:
        return data['cameraId']
