from Modules.VegetationIndex.Multispectral import Multispectral
import os
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from tifffile import imwrite


class Playground():

    def __init__(self):

        load_dotenv()
        self.__init_paths__()

    def __init_paths__(self):

        self.__init_input_paths__()
        self.__init_output_paths__()

    def __init_input_paths__(self):

        self.redDirectory = os.path.join(
            os.getenv('DATA_BASE_PATH'), os.getenv("RED_DIR"), "Train_Images")
        self.nirDirectory = os.path.join(
            os.getenv('DATA_BASE_PATH'), os.getenv("NIR_DIR"), "Train_Images")
        self.greenDirectory = os.path.join(
            os.getenv('DATA_BASE_PATH'), os.getenv("GREEN_DIR"), "Train_Images")
        self.redEdgeDirectory = os.path.join(
            os.getenv('DATA_BASE_PATH'), os.getenv("RED_EDGE_DIR"), "Train_Images")

    def __init_output_paths__(self):

        self.output_base = os.getenv('OUTPUT_BASE_PATH')

        if (os.path.exists(self.output_base) != True):
            os.mkdir(self.output_base)

    def plotResult(self, img, save=False):
        fig = plt.figure()
        plt.imshow(img, cmap=('RdYlGn'))
        plt.colorbar()
        plt.show()

        if (save):
            file_name = os.path.join(self.output_base, "test.png")
            fig.savefig(file_name, bbox_inches='tight')