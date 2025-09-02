def create_name(descriptor: str, params) -> str:
    name = descriptor.replace("(", "").replace(")", "")
    name = name.replace(".", "_").replace(" ", "_")

    for param in params:
        if param.is_dataset_parameter():
            if param.contains_list_of_datasets:
                names = [ds.name.replace(".", "_") for ds in param.dataset]
                name += "_" + "_".join(names)
            else:
                name += "_" + param.dataset.name.replace(".", "_")
            break  # nur erstes Dataset verwenden

    return name






