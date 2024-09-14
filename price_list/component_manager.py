from price_list.models import Component


class ComponentManager():
    """менеджер по работе с моделью Components основные CRUD операции"""

    @staticmethod
    def get_component_all()->dict:
        pass

    @staticmethod
    def get_component_by_art()->dict:
        pass

    @staticmethod
    def get_component_by_name()->dict:
        pass

    @staticmethod
    def get_component_by_lens_and_category()->dict:
        pass

    @staticmethod
    def get_component_image_by_art()->str:
        pass

    @staticmethod
    def add_new_component(art,name,price,category,url_image,lens)->bool:
        pass

    @staticmethod
    def update_component_by_art(art)->bool:
        pass
    
    @staticmethod
    def delete_component_by_art()->bool:
        pass


class LoaderComponent():
    pass