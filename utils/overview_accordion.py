import dash_mantine_components as dmc
from dash import html

characters_list = [
    {
        "id": "anxiety",
        "image": "https://img.icons8.com/external-flaticons-lineal-color-flat-icons/64/external-anxiety-psychology"
                 "-flaticons-lineal-color-flat-icons-2.png",
        "label": "Troubles anxieux",
        "description": "Variétés et impact",
        "content": "Les troubles anxieux englobent un ensemble de troubles de santé mentale caractérisés par une "
                   "anxiété et une peur significatives. Ces troubles peuvent se manifester sous forme d'anxiété "
                   "généralisée, de crises de panique, de phobies spécifiques, d'anxiété sociale, et plus encore. Les "
                   "symptômes courants incluent des inquiétudes excessives, de l'agitation et des difficultés de "
                   "concentration, affectant souvent les activités quotidiennes.",
    },
    {
        "id": "depressive",
        "image": "https://img.icons8.com/external-soft-fill-juicy-fish/60/external-depression-bankruptcy-soft-fill"
                 "-soft-fill-juicy-fish.png",
        "label": "Troubles dépressifs",
        "description": "Plus que de la tristesse",
        "content": "Les troubles dépressifs représentent un groupe de conditions marquées par des sentiments persistants "
                   "de tristesse et de perte d'intérêt. La dépression majeure, le trouble dépressif persistant et le "
                   "trouble affectif saisonnier figurent parmi les types. Les symptômes peuvent varier mais incluent "
                   "souvent des changements dans le sommeil, l'appétit, le niveau d'énergie et l'estime de soi.",
    },
    {
        "id": "bipolar",
        "image": "https://img.icons8.com/external-flaticons-lineal-color-flat-icons/64/external-bipolar-psychology"
                 "-flaticons-lineal-color-flat-icons-3.png",
        "label": "Trouble bipolaire",
        "description": "Les hauts et les bas de l'humeur",
        "content": "Le trouble bipolaire est caractérisé par des sautes d'humeur extrêmes, des phases maniaques "
                   "aux phases dépressives. Ces changements d'humeur, de niveau d'énergie et d'activité peuvent "
                   "affecter la capacité d'une personne à accomplir ses tâches quotidiennes. Le diagnostic et la "
                   "prise en charge nécessitent une approche prudente et globale.",
    },
    {
        "id": "schizophrenia",
        "image": "https://img.icons8.com/external-flaticons-lineal-color-flat-icons/64/external-schizophrenia"
                 "-psychology-flaticons-lineal-color-flat-icons-3.png",
        "label": "Trouble schizophrénique",
        "description": "Complexité de la pensée et de la perception",
        "content": "La schizophrénie est un trouble mental complexe et chronique caractérisé par des perturbations de la "
                   "pensée, de la perception et du comportement. Elle se manifeste souvent par des symptômes tels que des "
                   "hallucinations, des délires et une pensée désorganisée, impactant profondément le fonctionnement "
                   "quotidien.",
    },
    {
        "id": "eating",
        "image": "https://img.icons8.com/external-flaticons-lineal-color-flat-icons/64/external-eating-disorder"
                 "-psychology-flaticons-lineal-color-flat-icons-2.png",
        "label": "Troubles alimentaires",
        "description": "Complexités du comportement alimentaire",
        "content": "Les troubles alimentaires sont des affections graves affectant les comportements alimentaires, les "
                   "pensées et les émotions associées. Les types courants incluent l'anorexie mentale, la boulimie "
                   "mentale et le trouble de l'hyperphagie boulimique. Ces troubles peuvent avoir des impacts "
                   "physiques et psychologiques importants et nécessitent souvent un traitement complet."
    }
]


def create_accordion_label(label, image, description):
    return dmc.AccordionControl(
        dmc.Group(
            [
                dmc.Avatar(src=image, radius="xl", size="lg"),
                html.Div(
                    [
                        dmc.Text(label),
                        dmc.Text(description, size="sm", weight=400, color="dimmed"),
                    ]
                ),
            ]
        )
    )


def create_accordion_content(content):
    return dmc.AccordionPanel(dmc.Text(content, size="sm"))


disorders_accordion = dmc.Accordion(
    chevronPosition="right",
    variant="contained",
    children=[
        dmc.AccordionItem(
            [
                create_accordion_label(
                    character["label"], character["image"], character["description"]
                ),
                create_accordion_content(character["content"]),
            ],
            value=character["id"],
        )
        for character in characters_list
    ],
)
