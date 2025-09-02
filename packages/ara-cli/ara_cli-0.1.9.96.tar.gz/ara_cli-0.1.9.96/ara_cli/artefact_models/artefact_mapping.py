from ara_cli.artefact_models.artefact_model import ArtefactType
from ara_cli.artefact_models.businessgoal_artefact_model import BusinessgoalArtefact
from ara_cli.artefact_models.capability_artefact_model import CapabilityArtefact
from ara_cli.artefact_models.epic_artefact_model import EpicArtefact
from ara_cli.artefact_models.example_artefact_model import ExampleArtefact
from ara_cli.artefact_models.feature_artefact_model import FeatureArtefact
from ara_cli.artefact_models.issue_artefact_model import IssueArtefact
from ara_cli.artefact_models.keyfeature_artefact_model import KeyfeatureArtefact
from ara_cli.artefact_models.task_artefact_model import TaskArtefact
from ara_cli.artefact_models.userstory_artefact_model import UserstoryArtefact
from ara_cli.artefact_models.vision_artefact_model import VisionArtefact


title_prefix_to_artefact_class = {
    BusinessgoalArtefact._title_prefix(): BusinessgoalArtefact,
    CapabilityArtefact._title_prefix(): CapabilityArtefact,
    EpicArtefact._title_prefix(): EpicArtefact,
    ExampleArtefact._title_prefix(): ExampleArtefact,
    FeatureArtefact._title_prefix(): FeatureArtefact,
    IssueArtefact._title_prefix(): IssueArtefact,
    KeyfeatureArtefact._title_prefix(): KeyfeatureArtefact,
    TaskArtefact._title_prefix(): TaskArtefact,
    UserstoryArtefact._title_prefix(): UserstoryArtefact,
    VisionArtefact._title_prefix(): VisionArtefact
}


artefact_type_mapping = {
    ArtefactType.vision: VisionArtefact,
    ArtefactType.businessgoal: BusinessgoalArtefact,
    ArtefactType.capability: CapabilityArtefact,
    ArtefactType.epic: EpicArtefact,
    ArtefactType.userstory: UserstoryArtefact,
    ArtefactType.example: ExampleArtefact,
    ArtefactType.keyfeature: KeyfeatureArtefact,
    ArtefactType.feature: FeatureArtefact,
    ArtefactType.task: TaskArtefact,
    ArtefactType.issue: IssueArtefact
}