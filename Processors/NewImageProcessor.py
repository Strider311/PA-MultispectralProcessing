from Modules.ImageSaver import ImageSaver
from Modules.VegetationIndex.MultispectralFactory import MultispectralFactory
from Modules.Messaging.NewImageReceiver import NewImageReceiver
from Modules.Messaging.ProcessedImageSender import ProcessedImageSender
from dto.IncomingMessageDTO import IncomingMessageDTO
from dto.ProcessedImageDTO import ProcessedImageDTO
from dto.UpdateImageRequest import UpdateImageRequest
from dto.UpdateSessionPathRequest import UpdateSessionPathRequest
import logging
import json
from Exceptions.ImageDtoMapException import ImageDtoMapException
from Enums.MultiSpectralEnum import MultiSpectralEnum
import os
import requests


class NewImageProcessor():

    def __init__(self):
        self.__init_logger__()
        self.is_session_registered = False
        self.headers = {'Content-type': 'application/json'}
        self.new_image_url = f"{os.getenv('API_BASE')}{os.getenv('NEW_IMAGE_ENDPOINT')}"
        self.sessions_url = f"{os.getenv('API_BASE')}{os.getenv('NEW_SESSION_ENDPOINT')}"
        self.image_sender = ProcessedImageSender()
        self.image_saver = ImageSaver()
        self.multispectral = MultispectralFactory()
        self.message_receiver = NewImageReceiver(
            self.handle_new_message)

    def __init_logger__(self):
        logging.getLogger("matplotlib").setLevel(logging.WARNING)
        logging.getLogger("PIL").setLevel(logging.WARNING)
        self.logger = logging.getLogger('Main.Processor')
        self.logger.setLevel(logging.DEBUG)

    def handle_new_message(self, ch, method, properties, body):
        body_json = json.loads(body.decode())

        try:
            message = IncomingMessageDTO(
                id=body_json['id'],
                fileName=body_json['fileName'],
                dt_processed=body_json['dt_processed'],
                session_id=body_json['session_id']
            )

        except Exception:
            raise ImageDtoMapException("Unable to map incoming image")

        if not (self.is_session_registered):
            request = UpdateSessionPathRequest(
                self.image_saver.directory_manager.session_dir).toJSON()
            url = self.sessions_url + "/" + message.session_id
            response = requests.put(
                url, request, headers=self.headers)
            self.is_session_registered = True

        self.logger.info(
            f"[x] New Image: filename: {message.fileName} \nid: {message.id}")

        self.process_message(message)

    def process_message(self, new_image: IncomingMessageDTO):
        indices = []
        for multispectral_index in MultiSpectralEnum:
            self.__process_image__(new_image, multispectral_index)
            indices.append(multispectral_index.name)

        update_image_request = UpdateImageRequest().toJSON()
        image_id = new_image.id.replace('"', '')
        url = f"{self.new_image_url}/{image_id}"
        response = requests.put(
            url, update_image_request, headers=self.headers)

        processed_image = ProcessedImageDTO(fileName=new_image.fileName, id=new_image.id.replace('"', ''), session_id=new_image.session_id,
                                            session_dir=self.image_saver.directory_manager.session_dir, indices=indices,)
        self.image_sender.publish_new_image(processed_image)

        if (response.status_code != 200):
            raise Exception("Unable to update image state")

    def __process_image__(self, new_image: IncomingMessageDTO, multispectral_index: MultiSpectralEnum):
        self.logger.info(
            f"Processing {new_image.fileName} in {multispectral_index.name} index")
        image = self.multispectral.process(
            new_image.fileName, multispectral_index)

        self.image_saver.save_image(image, new_image,
                                    processing_type=multispectral_index)
