from .browser_encoder import BrowserDataEncoder
from .messenger_encoder import MessengerEncoder
from .deleted_encoder import DeletedDataEncoder
from .usb_encoder import UsbDataEncoder
from .lnk_encoder import LnkDataEncoder
from .prefetch_encoder import PrefetchEncoder
from ..core import Category, BaseDataEncoder

class Encoder:
    def __init__(self) -> None:
        self.browser:BrowserDataEncoder = BrowserDataEncoder()
        self.deleted:DeletedDataEncoder = DeletedDataEncoder()
        self.lnk:LnkDataEncoder = LnkDataEncoder()
        self.messenger:MessengerEncoder = MessengerEncoder()
        self.prefetch:PrefetchEncoder = PrefetchEncoder()
        self.usb:UsbDataEncoder = UsbDataEncoder()

    def _get_encoder(self, category:Category) -> BaseDataEncoder:
        match category:
            case Category.BROWSER:
                return self.browser
            case Category.DELETED:
                return self.deleted
            case Category.LNK:
                return self.lnk
            case Category.MESSENGER:
                return self.messenger
            case Category.PREFETCH:
                return self.prefetch
            case Category.USB:
                return self.usb
            case _:
                raise TypeError

    def convert_data(self, data:dict, category:Category) -> BaseDataEncoder:
        encoder = self._get_encoder(category)
        encoder.convert_data(data)
        return encoder