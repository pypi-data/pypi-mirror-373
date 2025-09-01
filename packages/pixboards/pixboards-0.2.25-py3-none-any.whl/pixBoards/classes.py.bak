import os
from datetime import date

from pixBoards.config_loader import config
from pixBoards.log_utils import setup_logger

# set up logger
today = date.today()
logger = setup_logger(__name__)

# masterDir = config["masterDir"]

padding = config["padding"]
imgs_per_page = config["page_size"]
# print(f'imgs per page are {imgs_per_page}'  )


class page:
    def __init__(self, page_number, total_pages, images, file_location, bname):
        self.page_number = page_number  # Current page number
        self.images = images  # image list for the page
        self.total_pages = total_pages
        self.file_location = file_location
        self.bname = bname


from math import ceil


class board:
    def __init__(
        self,
        name,
        output_file_loc,
        image_paths,
        # no_of_imgs,
        paginate=True,
        upload=False,
        dummy_status=False,
        img_list_status=False,
    ):
        self.name = name
        self.image_paths = image_paths
        self.pages = []  # will be storing a list of instances of class, page.
        self.imgs_per_page = imgs_per_page
        self.output_file_loc = output_file_loc
        self.upload_status = upload
        self.paginate_status = paginate
        self.link_hash_map = {} if self.upload_status else None
        self.no_of_imgs = len(image_paths)
        self.nested_boards = []
        self.dummy_status = dummy_status
        self.img_list_status = img_list_status
        parts = self.name.split("_~")
        self.clean_name = parts[-1]
        self.parent = "_~".join(parts[:-1])

    def paginate_board(self):
        total_images = len(self.image_paths)
        # logger.info(f'total images = {total_images}')
        total_pages = ceil(total_images / self.imgs_per_page)
        output_base = self.output_file_loc
        for i in range(total_pages):

            start = i * self.imgs_per_page
            end = start + self.imgs_per_page
            page_images = self.image_paths[start:end]
            file_loc = (
                os.path.join(output_base, self.name) + f"_{(i+1):0{padding}}.html"
            )
            Page = page(
                page_number=i + 1,
                total_pages=total_pages,
                images=page_images,
                file_location=file_loc,
                bname=self,
            )
            self.pages.append(Page)
            logger.debug(
                f"Finished with - Board: {self.name}, page {i + 1} of {total_pages}"
            )
