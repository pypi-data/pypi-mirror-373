class ColumnStrings:
    """Фиксированные имена столбцов"""
    PRC: str = "__proceed"
    RMK: str = "__remark"

    CONFIG_SUBSTRING: str = "substring"
    CONFIG_ENTITIER: str = "entitier"
    CONFIG_TARGET_RESULT: str = "target_result"
    CONFIG_VALUE: str = "value"

    REGISTRY_CAT_ID: str = "cat_id"
    REGISTRY_STATUS: str = "status"
    REGISTRY_STATUS_DONE: str = "done"
    REGISTRY_STATUS_WAIT: str = "wait"
    REGISTRY_STATUS_PROCESS: str = "process"
    REGISTRY_STAGE: str = "stage"

    @classmethod
    def skip_status(cls, status: str):
        return status in [
            cls.REGISTRY_STATUS_DONE,
            cls.REGISTRY_STATUS_WAIT,
        ]

    TEMPLATE_CAT_ID: str = "cat_id"
    TEMPLATE_FINALIZE_FIELDS: str = "finalize_fields"
    TEMPLATE_CATEGORY_NAME: str = "category_name"
    TEMPLATE_CASTRATOR_FIELDS: str = "castrator_fields"
    TEMPLATE_CATEGORY_ALIAS: str = "category_alias"
    TEMPLATE_INSTRUCTIONS: str = "instructions"
    TEMPLATE_SCHEMA: str = "schema"

    SCHEMA_NAME: str = "name"
    SCHEMA_DESCRIPTION: str = "description"
    SCHEMA_VALUES: str = "values"
    SCHEMA_INSTRUCTION: str = "instruction"
    SCHEMA_INSTRUCTION_ASIS: str = "instruction_asis"
    SCHEMA_INSTRUCTION_TOBE: str = "instruction_tobe"
    SCHEMA_EXAMPLES: str = "examples"

    DATA_LOCAL_ID: str = "local_id"

    DATA_SOURCE_NAME: str = "source_name"
    DATA_URL: str = "url"

    DATA_ENTITY_ASIS: str = "entity_asis"
    DATA_ENTITY_TOBE: str = "entity_tobe"

    DATA_BRAND_ASIS: str = "brand_asis"
    DATA_BRAND_TOBE: str = "brand_tobe"

    DATA_MODEL_ASIS: str = "model_asis"
    DATA_MODEL_TOBE: str = "model_tobe"

    DATA_PROCESSOR_ASIS: str = "processor_asis"
    DATA_PROCESSOR_TOBE: str = "processor_tobe"

    DATA_RAM_ASIS: str = "ram_asis"
    DATA_RAM_TOBE: str = "ram_tobe"

    DATA_SSDHDD_ASIS: str = "ssd_hdd_capacity_asis"
    DATA_SSDHDD_TOBE: str = "ssd_hdd_capacity_tobe"

    DATA_VIDEOCARD_ASIS: str = "videocard_asis"
    DATA_VIDEOCARD_TOBE: str = "videocard_tobe"

    DATA_POWER_KWT_ASIS: str = "power_asis"
    DATA_POWER_KWT_TOBE: str = "power_tobe"

    DATA_COLOR_ASIS: str = "color_asis"
    DATA_COLOR_TOBE: str = "color_tobe"

    DATA_DIAGONAL_ASIS: str = "diagonal_asis"
    DATA_DIAGONAL_TOBE: str = "diagonal_tobe"

    DATA_KIT_ASIS: str = "kit_asis"
    DATA_KIT_TOBE: str = "kit_tobe"

    DATA_PACK_ASIS: str = "pack_asis"
    DATA_PACK_TOBE: str = "pack_tobe"

    DATA_L_VOLUME_ASIS: str = "volume_asis"
    DATA_L_VOLUME_TOBE: str = "volume_tobe"

    DATA_SIZE_ASIS: str = "size_asis"
    DATA_SIZE_TOBE: str = "size_tobe"

    DATA_FREQUENCY_ASIS: str = "frequency_asis"
    DATA_FREQUENCY_TOBE: str = "frequency_tobe"

    DATA_GEN_ASIS: str = "gen_asis"
    DATA_GEN_TOBE: str = "gen_tobe"

    DATA_LENGTH_ASIS: str = "length_asis"
    DATA_LENGTH_TOBE: str = "length_tobe"

    DATA_NUMBER_OF_SOCKETS_ASIS: str = "number_of_sockets_asis"
    DATA_NUMBER_OF_SOCKETS_TOBE: str = "number_of_sockets_tobe"

    DATA_DIAMETER_ASIS = "diameter_asis"
    DATA_DIAMETER_TOBE = "diameter_tobe"

    DATA_QUANTITY_ASIS = "quantity_asis"
    DATA_QUANTITY_TOBE = "quantity_tobe"
