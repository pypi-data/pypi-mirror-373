import unittest

from spypointapi.shared_cameras.shared_cameras_api_response import SharedCamerasApiResponse


class TestSharedCamerasApiResponse(unittest.TestCase):

    def test_parses_camera_ids_from_json(self):
        camera_ids = SharedCamerasApiResponse.from_json([
            {
                "sharedCameras": [
                    {"cameraId": "id1"},
                    {"cameraId": "id2"},
                    {"cameraId": "id3"},
                ]
            }
        ])

        self.assertEqual(camera_ids, ["id1", "id2", "id3"])

    def test_parses_no_shared_cameras_from_json(self):
        camera_ids = SharedCamerasApiResponse.from_json([])

        self.assertEqual(camera_ids, [])
