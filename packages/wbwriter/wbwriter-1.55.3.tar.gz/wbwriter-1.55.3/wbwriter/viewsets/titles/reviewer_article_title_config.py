from wbcore.metadata.configs.titles import TitleViewConfig


class ReviewerArticleTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Articles to be reviewed"
