import dash
from dash import dcc, html, Output, Input, State, clientside_callback, ClientsideFunction
import dash_mantine_components as dmc
from dash_iconify import DashIconify

GITHUB = 'https://github.com/lemarouane'
CONTACT_ICON_WIDTH = 30


def modal_data_source():
    return dmc.Modal(
        id='modal-data-source',
        size='55%',
        styles={
            'modal': {
                'background-color': '#f2f2f2',
            }
        },
        children=[
            dcc.Markdown(
                [
                    """
                    
                    # À propos de l'ensemble de données
                    
                    La santé mentale est un aspect crucial de nos vies et de la société, influençant le bien-être, 
                    la capacité de travail et les relations avec les amis, la famille et la communauté. Des centaines de 
                    millions de personnes souffrent de troubles mentaux chaque année, environ 1 femme sur 3 et 1 homme sur 
                    5 connaissant une dépression majeure au cours de leur vie. D'autres affections, comme la schizophrénie 
                    et le trouble bipolaire, bien que moins courantes, ont également un impact significatif sur la vie des gens.
                    
                    Alors que les maladies mentales sont traitables et que leur impact peut être réduit, le traitement est 
                    souvent insuffisant ou de mauvaise qualité. De nombreux individus se sentent également mal à l'aise de 
                    partager leurs symptômes avec des professionnels de la santé ou des connaissances, ce qui rend difficile 
                    une estimation précise de la prévalence de ces affections.
                    
                    Pour soutenir et traiter efficacement les troubles de santé mentale, des données complètes et fiables sont 
                    essentielles. Cet ensemble de données vise à fournir des informations sur la manière, le moment et la 
                    raison de l'apparition de ces affections, leur prévalence et les méthodes de traitement efficaces.
                    
                    ## Informations sur la source
                    
                    - **Développement :** Marouane Haddad (Lors de son Projet de fin d'études) 
                    - **Titre :** "Mental Health"
                    - **Publié en ligne :** en cours
                    - **Obtenu à partir de :** [Ensemble de données Kaggle](https://www.kaggle.com/datasets/amirhoseinmousavian/mental-health)
                    - **Couverture temporelle :** Du 31/12/1989 au 31/12/2020
                    - **Couverture géospatiale :** Mondiale
                    
                    
                    ## Méthodologie de collecte
                    
                    Les données ont été collectées en visitant l'éditeur et comprennent des informations provenant des enquêtes 
                    mondiales sur la santé mentale menées entre 2001 et 2015.
                    
                    """
                ],
            )
        ]
    )


header = html.Div(
    dmc.Grid(
        [
            modal_data_source(),
            dmc.Col(
                [
                    dmc.Group(
                        [
                            dmc.ActionIcon(
                                [
                                    DashIconify(icon='bx:data', color='#C8C8C8', width=25)
                                ],
                                variant='transparent',
                                id='about-data-source'
                            ),
                            dmc.Anchor(
                                [
                                    DashIconify(icon='uil:github', color='#8d8d8d', width=CONTACT_ICON_WIDTH),
                                ],
                                href=GITHUB
                            )
                        ],
                        spacing='xl',
                        position='right'
                    )
                ],
                offsetMd=1,
                md=10,
            )
        ],
        mt='md',
        mb=35
    )
)


clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='toggle_modal_data_source'),
    Output('modal-data-source', 'opened'),
    Input('about-data-source', 'n_clicks'),
    State('modal-data-source', 'opened')
)
