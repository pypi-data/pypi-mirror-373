from omegaconf import DictConfig
from torch.utils.data import Dataset
from tqdm import tqdm

from characterization.features import BaseFeature
from characterization.scorer.base_scorer import BaseScorer
from characterization.utils.io_utils import get_logger, to_pickle
from characterization.schemas import ScenarioFeatures
from characterization.processors.base_processor import BaseProcessor

logger = get_logger(__name__)


class FeatureProcessor(BaseProcessor):
    def __init__(
        self,
        config: DictConfig,
        dataset: Dataset,
        characterizer: BaseFeature | BaseScorer,
    ) -> None:
        """Initializes the FeatureProcessor with configuration, dataset, and feature characterizer.

        Args:
            config (DictConfig): Configuration for the feature processor, including parameters such as
                batch size, number of workers, shuffle, save, and output path.
            dataset (Dataset): The dataset to process. Must be a subclass of torch.utils.data.Dataset.
            characterizer (BaseFeature | BaseScorer): An instance of BaseFeature or BaseScorer that
                defines the feature computation logic.

        Raises:
            AssertionError: If the characterizer is not of type 'feature'.
        """
        super(FeatureProcessor, self).__init__(config, dataset, characterizer)
        if not self.characterizer.characterizer_type == "feature":
            raise AssertionError(
                f"Expected characterizer of type 'feature', got {self.characterizer.characterizer_type}.",
            )

    def run(self):
        """Runs the feature processing on the dataset.

        Iterates over the dataset and computes features for each scenario using the characterizer.
        If saving is enabled, features are serialized and saved to disk.

        Returns:
            None
        """
        logger.info(f"Processing {self.characterizer.name} for {self.dataset.name}.")

        # TODO: Need more elegant iteration over the dataset to avoid the two-level for loop.
        # for scenario_batch in track(self.dataloader, total=len(self.dataloader), description="Processing features"):
        for scenario_batch in tqdm(self.dataloader, total=len(self.dataloader), desc="Processing features..."):
            for scenario in scenario_batch["scenario"]:
                features: ScenarioFeatures = self.characterizer.compute(scenario)  # pyright: ignore[reportCallIssue]

                if self.save:
                    to_pickle(self.output_path, features.model_dump(), scenario.metadata.scenario_id)

        logger.info(f"Finished processing {self.characterizer.name} features for {self.dataset.name}.")
