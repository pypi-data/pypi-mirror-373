from dataclasses import dataclass, field, asdict

from nemo_library.utils.utils import get_display_name, get_import_name, get_internal_name


@dataclass
class MigMan:
    project: str = None
    postfix: str = None
    index : int = None
    desc_section_column: str = None
    desc_section_column_name: str = None
    desc_section_location_in_proalpha: str = None
    desc_section_data_type: str = None
    desc_section_format: str = None
    header_section_label: str = None
    nemo_display_name: str = None
    nemo_internal_name: str = None
    nemo_import_name: str = None
    snow_remark: list[str] = field(default_factory=list)
    snow_appguide_text: str = None
    snow_appguide_link: str = None
    snow_update: bool = None
    snow_mandatory: bool = None
    snow_ref: bool = None
    snow_relevance: bool = None
    
    def to_dict(self):
        """
        Converts the Page instance to a dictionary.

        Returns:
            dict: A dictionary representation of the Page instance.
        """
        return asdict(self)
    
    def __post_init__(self):
        """
        Post-initialization processing to set the internal and import names if not provided.
        """
        self.postfix = self.postfix if self.postfix != "MAIN" else ""
        self.desc_section_data_type = self.desc_section_data_type.lower()
        if not self.nemo_display_name:
            self.nemo_display_name = get_display_name(self.desc_section_location_in_proalpha, self.index)
        if not self.nemo_internal_name:
            self.nemo_internal_name = get_internal_name(self.desc_section_location_in_proalpha, self.index)            
        if not self.nemo_import_name:
            self.nemo_import_name = get_import_name(self.desc_section_location_in_proalpha, self.index)                        