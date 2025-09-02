from typing import Optional

from django.utils.translation import gettext as _
from wbcore.contrib.color.enums import WBColor
from wbcore.contrib.icons import WBIcon
from wbcore.enums import Operator, Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display import (
    Display,
    Inline,
    Layout,
    Page,
    Section,
    Style,
)
from wbcore.metadata.configs.display.instance_display.operators import default
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbwriter.models import Article


class DependantArticleDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> dp.ListDisplay:
        article = "dependant_article" if "article_id" in self.view.kwargs else "article"
        return dp.ListDisplay(
            fields=[
                dp.Field(key=article, label=_("Article")),
            ]
        )


class ArticleDisplayConfig(DisplayViewConfig):
    """Provides getter methods for the list and instance displays."""

    def get_instance_display(self) -> Display:
        using_section = Section(
            key="using_section",
            title=_("Uses Articles"),
            collapsible=False,
            display=Display(
                pages=[
                    Page(
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["dependantarticle-article"]],
                                inlines=[
                                    Inline(key="dependantarticle-article", endpoint="dependantarticle-article"),
                                ],
                            )
                        },
                    )
                ]
            ),
        )

        used_section = Section(
            key="used_section",
            title=_("Used in Articles"),
            collapsible=False,
            display=Display(
                pages=[
                    Page(
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["usedarticle-article"]],
                                inlines=[
                                    Inline(key="usedarticle-article", endpoint="usedarticle-article"),
                                ],
                            )
                        },
                    )
                ]
            ),
        )

        status_section = Section(
            key="status_section",
            title=_("Status"),
            collapsible=False,
            display=Display(
                pages=[
                    Page(
                        title=_("Status"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["status"]],
                                grid_template_columns="auto-fill",
                            )
                        },
                    )
                ]
            ),
        )

        permission_section = Section(
            key="permission_section",
            title=_("Author & Reviewers"),
            collapsed=True,
            display=Display(
                pages=[
                    Page(
                        title=_("Author & Reviewers"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["author", "reviewer"], ["peer_reviewer", "qa_reviewer"]],
                                grid_template_columns=[Style.fr(1), Style.fr(1)],
                                grid_auto_rows=Style.MIN_CONTENT,
                            )
                        },
                    )
                ]
            ),
        )

        additional_information_section = Section(
            key="additional_information_section",
            title=_("Additional Information"),
            display=Display(
                pages=[
                    Page(
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["information"]],
                                inlines=[Inline(key="information", endpoint="metainformationinstance")],
                            )
                        }
                    )
                ]
            ),
        )

        def _get_instance_display(
            collapsed_metadata_section: bool = False,
            collapsed_content_section: bool = False,
            show_is_private: bool = False,
            show_with_additional_information: bool = False,
        ) -> Display:
            """Returns a display for the wbwriter instance

            Args:
                collapsed_metadata_section: Indicates whether the metadata section should be collapsed. Defaults to False.
                collapsed_content_section: Indicates whether the content section should be collapsed. Defaults to False.
                show_is_private: Indicates whether the is_private field should be visible. Defaults to False.
                show_with_additional_information: Indicates whether the additional_information section should be added to the display. Defaults to False.

            Returns:
                Display: A display instance
            """

            def _metadata_section(collapsed: bool = True, show_is_private: bool = False) -> Section:
                """Returns the metadata section

                Args:
                    collapsed: Indicates whether the section should be collapsed or not. Defaults to True.
                    show_is_private: Indicates whether the is_private field should be visible or not. Defaults to False.

                Returns:
                    Section: A section instance
                """

                grid_template = [
                    ["teaser_image", "type", "is_private"] if show_is_private else ["teaser_image", "type", "."],
                    ["teaser_image", "name", "title"],
                    ["teaser_image", "modified", "created"],
                ]
                return Section(
                    key="metadata_section",
                    title=_("Metadata"),
                    collapsible=True,
                    collapsed=collapsed,
                    display=Display(
                        pages=[
                            Page(
                                title=_("Metadata"),
                                layouts={
                                    default(): Layout(
                                        grid_template_areas=grid_template,
                                        grid_template_columns=[Style.MIN_CONTENT, Style.fr(1), Style.fr(1)],
                                        grid_auto_rows=Style.MIN_CONTENT,
                                    ),
                                },
                            )
                        ]
                    ),
                )

            def _content_section(collapsed: bool) -> Section:
                """Returns the content section

                Args:
                    collapsed: Indicates whether the section should be collapsed or not. Defaults to False.

                Returns:
                    Section: A section instance
                """

                return Section(
                    key="content_section",
                    title=_("Content & Tags"),
                    collapsed=collapsed,
                    display=Display(
                        pages=[
                            Page(
                                title=_("Content & Tags"),
                                layouts={
                                    default(): Layout(
                                        grid_template_areas=[["tags"], ["content"]],
                                        grid_template_columns=[Style.fr(1)],
                                        grid_auto_rows=Style.MIN_CONTENT,
                                    ),
                                },
                            )
                        ]
                    ),
                )

            sections = [
                status_section,
                _metadata_section(collapsed_metadata_section, show_is_private),
                _content_section(collapsed_content_section),
                permission_section,
                used_section,
                using_section,
            ]
            grid_template = [
                ["status_section", "status_section"],
                ["metadata_section", "metadata_section"],
                ["content_section", "content_section"],
                ["permission_section", "permission_section"],
                ["using_section", "used_section"],
            ]

            if show_with_additional_information:
                sections.append(additional_information_section)
                grid_template.append(["additional_information_section", "additional_information_section"])

            return Display(
                pages=[
                    Page(
                        title=_("General Information"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=grid_template,
                                grid_auto_rows=Style.MIN_CONTENT,
                                sections=sections,
                            ),
                        },
                    ),
                ]
            )

        if self.view.kwargs.get("pk"):
            obj: Article = self.view.get_object()
            if obj.status in [Article.Status.APPROVED, Article.Status.PUBLISHED]:
                if self.request.user.has_perm("wbwriter.administrate_article"):
                    return _get_instance_display(
                        collapsed_content_section=True, show_is_private=True, show_with_additional_information=True
                    )
                return _get_instance_display(collapsed_content_section=True)
            return _get_instance_display(collapsed_metadata_section=True)
        return _get_instance_display()

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        """Sets up and returns the list display for Article."""
        return dp.ListDisplay(
            fields=[
                dp.Field(key="is_private_icon", label=" ", width=Unit.PIXEL(40)),
                dp.Field(key="id", label=_("ID")),
                dp.Field(key="title", label=_("Title")),
                dp.Field(key="teaser_image", label=_("Teaser image")),
                dp.Field(key="type", label=_("Type")),
                dp.Field(key="modified", label=_("Last Modification Date")),
                dp.Field(key="created", label=_("Creation Date")),
                dp.Field(key="tags", label=_("Tags")),
                dp.Field(key="author", label=_("Author")),
                dp.Field(key="reviewer", label=_("Reviewer")),
                dp.Field(key="peer_reviewer", label=_("Peer Reviewer")),
                dp.Field(key="qa_reviewer", label=_("QA Reviewer")),
            ],
            formatting=[
                dp.Formatting(
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.YELLOW.value},
                            condition=dp.Condition(
                                operator=Operator.EQUAL,
                                value=Article.Status.DRAFT,
                            ),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.RED_DARK.value},
                            condition=dp.Condition(
                                operator=Operator.EQUAL,
                                value=Article.Status.FEEDBACK,
                            ),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.BLUE_LIGHT.value},
                            condition=dp.Condition(
                                operator=Operator.EQUAL,
                                value=Article.Status.PEER_REVIEW,
                            ),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.BLUE.value},
                            condition=dp.Condition(
                                operator=Operator.EQUAL,
                                value=Article.Status.QA_REVIEW,
                            ),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=dp.Condition(
                                operator=Operator.EQUAL,
                                value=Article.Status.AUTHOR_APPROVAL,
                            ),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN.value},
                            condition=dp.Condition(
                                operator=Operator.EQUAL,
                                value=Article.Status.APPROVED,
                            ),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_DARK.value},
                            condition=dp.Condition(
                                operator=Operator.EQUAL,
                                value=Article.Status.PUBLISHED,
                            ),
                        ),
                    ],
                    column="status",
                )
            ],
            legends=[
                dp.Legend(
                    key="status",
                    items=[
                        dp.LegendItem(
                            value=Article.Status.FEEDBACK.value,
                            label=Article.Status.FEEDBACK.label,
                            icon=WBColor.RED_DARK.value,
                        ),
                        dp.LegendItem(
                            value=Article.Status.DRAFT.value,
                            label=Article.Status.DRAFT.label,
                            icon=WBColor.YELLOW.value,
                        ),
                        dp.LegendItem(
                            value=Article.Status.PEER_REVIEW.value,
                            label=Article.Status.PEER_REVIEW.label,
                            icon=WBColor.BLUE_LIGHT.value,
                        ),
                        dp.LegendItem(
                            value=Article.Status.QA_REVIEW.value,
                            label=Article.Status.QA_REVIEW.label,
                            icon=WBColor.BLUE.value,
                        ),
                        dp.LegendItem(
                            value=Article.Status.AUTHOR_APPROVAL.value,
                            label=Article.Status.AUTHOR_APPROVAL.label,
                            icon=WBColor.GREEN_LIGHT.value,
                        ),
                        dp.LegendItem(
                            value=Article.Status.APPROVED.value,
                            label=Article.Status.APPROVED.label,
                            icon=WBColor.GREEN.value,
                        ),
                        dp.LegendItem(
                            value=Article.Status.PUBLISHED.value,
                            label=Article.Status.PUBLISHED.label,
                            icon=WBColor.GREEN_DARK.value,
                        ),
                    ],
                ),
                dp.Legend(
                    key="is_private",
                    items=[
                        dp.LegendItem(
                            value=False,
                            label=_("Public"),
                            icon=WBIcon.VIEW.icon,
                        ),
                        dp.LegendItem(
                            value=True,
                            label=_("Private"),
                            icon=WBIcon.IGNORE.icon,
                        ),
                    ],
                ),
            ],
        )
