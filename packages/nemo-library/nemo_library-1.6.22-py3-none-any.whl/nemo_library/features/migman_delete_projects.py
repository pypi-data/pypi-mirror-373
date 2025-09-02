from nemo_library.features.nemo_persistence_api import deleteProjects
from nemo_library.features.nemo_persistence_api import getProjects
from nemo_library.utils.config import Config
from nemo_library.utils.migmanutils import get_migman_project_list

__all__ = ["MigManDeleteProjects"]


def MigManDeleteProjects(config: Config) -> None:
    """
    Deletes projects from the system that match the MigMan project list.

    Args:
        config (Config): The configuration object containing necessary settings.

    This function retrieves all projects and filters them based on their display names
    to match the MigMan project list. It then deletes the matching projects.
    """
    nemo_projects = getProjects(config)
    migmanprojects = get_migman_project_list(config)
    migmanmappingfields = config.get_migman_mapping_fields()
    project_map = {project.displayName: project.id for project in nemo_projects}
    delete = []
    for project in migmanprojects:
        if project in project_map:
            delete.append(project_map[project])

    for mapping in migmanmappingfields:
        if f"Mapping {mapping}" in project_map:
            delete.append(project_map[f"Mapping {mapping}"])

    deleteProjects(config,delete)
    