# __init__.py
from .PixVerse_Extend_Node import PixVerseExtendNode
from .PixVerse_Generate_Node import PixVerseGenerateNode
from .PixVerse_Image_Upload_Node import PixVerseImageUploadNode
from .PixVerse_Text_To_Video_Node import PixVerseTextToVideoNode
from .PixVerse_Upload_Video_Node import PixVerseUploadVideoNode
from .PixVerse_Login import PixVerseLogin


NODE_CLASS_MAPPINGS = {
    "PixVerseExtendNode": PixVerseExtendNode,
    "PixVerseGenerateNode": PixVerseGenerateNode,
    "PixVerseImageUploadNode": PixVerseImageUploadNode,
    "PixVerseTextToVideoNode": PixVerseTextToVideoNode,
    "PixVerseUploadVideoNode": PixVerseUploadVideoNode,
    "PixVerseLogin": PixVerseLogin

}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PixVerseExtendNode": "🔁 PixVerse Extend Video",
    "PixVerseGenerateNode": "🎬 PixVerse I2V (con Créditos)",
    "PixVerseImageUploadNode": "📤 PixVerse Upload Image",
    "PixVerseTextToVideoNode": "🎬 PixVerse T2V (con Créditos)",
    "PixVerseUploadVideoNode": "📤 PixVerse Upload Video",
    "PixVerseLogin": "🔐 PixVerse Login (API)",
 
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
