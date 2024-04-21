import dash
import pandas as pd
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import html, dcc, callback, Input, Output, State, clientside_callback, no_update, Patch, ctx, \
    ClientsideFunction
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from utils.process_data import all_disorders_dataframes, country_code_to_continent_name, get_population_data
from utils.ga_utils import calculate_slope, make_edit_icon, get_last_added_entity, update_last_entity, filter_dataframe, \
    get_country_continent_name, create_country_title, update_no_data, clean_duplicated_columns
from utils.ga_choropleth import create_choropleth_fig
from utils.ga_heatmap import create_heatmap
from utils.ga_sankey import create_sankey
from utils.ga_tabs import tabs_heatmap, tabs_sankey
from utils.utils_config import FIG_CONFIG_WITH_DOWNLOAD, FIG_CONFIG_WITHOUT_DOWNLOAD, BG_TRANSPARENT, HIDE, \
    STORAGE_SESSION, add_loading_overlay

pd.set_option('display.float_format', '{}'.format)

all_continents = [
    continent
    for continent in all_disorders_dataframes['Anxiety'].prevalence_by_country['Continent'].unique()
    if continent != 'Unknown'
]

CHOROPLETH_INTERVAL = 50
SLIDER_YEAR_INCREMENT = 10
is_first_session = True

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

dash.register_page(
    __name__,
    path='/global-analysis',
    order=1,
    title='Mental Health - Prevalence Analysis',
    description="""
   Découvrez une analyse approfondie de la prévalence des troubles mentaux en fonction de la localisation, de l'âge et 
    du genre. Cette page interactive permet d'explorer les tendances en matière de santé mentale dans les pays, les 
    continents et les groupes démographiques.
    """,
    image='miniature.png'
)

layout = html.Div(
    [
        dmc.Grid(
            [
                dmc.Col(
                    [
                        dmc.Group(
                            [
                                create_country_title(text='Exploration des tendances en santé mentale dans', id='base-title'),
                                dmc.Group(
                                    [
                                        html.Div(id='country-title-container'),
                                        create_country_title(text=':'),
                                    ], spacing=1
                                ),
                                dmc.Select(
                                    id='select-disorder',
                                    value='Anxiety',
                                    data=sorted(
                                        [{'value': k, 'label': k} for k in all_disorders_dataframes.keys()],
                                        key=lambda x: x['value']
                                    ),
                                    size='md',
                                    variant='unstyled',
                                    style={'width': '12.5rem'},
                                    styles={
                                        'input': {
                                            'font-size': '1.5625rem',
                                            'color': '#4e3a8e',
                                            'font-weight': 'bold',
                                            'text-decoration': 'underline'
                                        },
                                        'item': {'font-size': '0.9rem'}
                                    },
                                    persistence=True,
                                    persistence_type=STORAGE_SESSION
                                ),
                            ],
                            position='left',
                            spacing=7
                        ),
                        dmc.Text(
                            'Plongez dans des catégories spécifiques pour découvrir comment la localisation, âge et le '
                            'sexe contribuent à la prévalence de divers troubles de santé mentale.',
                            align='justify',
                            color='#4B4B4B',
                            mt='md'
                        )
                    ],

                    offsetLg=1,
                    lg=6
                )
            ],
        ),
        dmc.Grid(
            [
                dmc.Col(
                    [
                        dmc.Tabs(
                            [
                                dmc.TabsList(
                                    [
                                        dmc.Tab('Tendances par pays et continent', value='heatmap'),
                                        dmc.Tab('Informations sur âge et le genre', value='sankey')
                                    ]
                                ),
                                dmc.TabsPanel(tabs_heatmap, value='heatmap'),
                                dmc.TabsPanel(tabs_sankey, value='sankey')
                            ],
                            value='heatmap',
                            color='grape'
                        ),
                        dmc.Divider(label='Quick Add: Select by Continent', mt='xl'),
dmc.Container(
    [
        dmc.MultiSelect(
            label=None,
            placeholder='Sélectionnez un continent..',
            id='select-continent',
            persistence=True,
            persistence_type='session',
            data=sorted([
                {'value': continent, 'label': continent} for continent in all_continents
            ], key=lambda x: x['value']),
            styles={
                'input': {
                    'background-color': 'rgba(0,0,0,0)',
                    'border': 'none',
                    'font-size': '1.5625rem',
                    'color': '#4e3a8e',
                    'font-weight': 'bold',
                },
                'item': {
                    'font-size': '0.9rem',
                }
            },
        )
    ],
    mt='lg',
    px=0
)

                    ],
                    offsetLg=1,
                    lg=6
                ),
dmc.Col(
    [
        dmc.Group(
            [
                make_edit_icon(
                    icon='lucide:undo',
                    id='del-last-selected-country',
                    tooltip='Supprimer le dernier pays ajouté'
                ),
                dmc.ActionIcon(
                    DashIconify(icon='ph:play-pause-light', width=35),
                    id='stop-interval',
                    variant='transparent'
                ),
                make_edit_icon(
                    icon='fluent:delete-12-regular',
                    id='del-all-selected-country',
                    color='red',
                    tooltip='Effacer tous les pays'
                )
            ],
            position='center',
            mb='xl'
        ),
        dmc.Center(
            [
                dmc.FloatingTooltip(
                    [
                        dmc.Container(
                            [
                                html.Div(
                                    [
                                        dmc.Center(
                                            [dmc.Loader(color='#967bb6')],
                                            style={'height': '100%'}
                                        )
                                    ],
                                    style={'height': '44vh'}
                                ),
                                dcc.Graph(id='choropleth-fig', style={'display': 'none'})
                            ],
                            id='choropleth-container',
                            px=0
                        )
                    ],
                    label=None,
                    color=BG_TRANSPARENT,
                    id='choropleth-tooltip'
                ),
            ]
        ),
        dmc.Container(
            id='range-slider-container',
            children=[dmc.Slider(id='year-slider', style=HIDE)],
            px=0,
            style={
                'display': 'flex',
                'flex-direction': 'column',
                'align-items': 'center',
            },
            mt=50,
        )
    ],
    lg=5
)

            ],
            mt=35,
            mb=100
        ),
        dcc.Store(id='disorder-data'),
        dcc.Store(id='average-prevalence-per-country'),
        dcc.Store(id='annual-prevalence-per-country'),
        dcc.Store(id='selected-entities', data={}, storage_type=STORAGE_SESSION),
        dcc.Store(id='last-entity-add', data=[], storage_type=STORAGE_SESSION),
        dcc.Store(id='cache-selected-continent', data=[], storage_type=STORAGE_SESSION),
        dcc.Store(id='sankey-data', data=[])
    ],
    id='global-analysis-container',
    className='animate__animated animate__fadeIn animate__slow'
)


@callback(
    Output('disorder-data', 'data'),
    Input('select-disorder', 'value')
)
def update_selected_disorder_data(disorder_name):
    """
    Mettre à jour les données relatives au trouble sélectionné (anxiété, bipolaire, ..)
    """
    return all_disorders_dataframes[disorder_name].prevalence_by_country.to_dict('records')


@callback(
    Output('range-slider-container', 'children'),
    Input('disorder-data', 'data'),
    State('select-disorder', 'value'),
    prevent_initial_call=True
)

def update_year_slider(_, disorder_name):
    """
    Mettre à jour le curseur de l'année en fonction de l'année minimale et maximale d'un trouble spécifique
    """
    disorder_df = all_disorders_dataframes[disorder_name].prevalence_by_country
    color = all_disorders_dataframes[disorder_name].pastel_color
    min_year, max_year = disorder_df['Year'].min(), disorder_df['Year'].max()

    return dmc.RangeSlider(
        id='year-slider',
        value=[min_year, max_year],
        min=min_year,
        max=max_year,
        minRange=1,
        marks=[
            {'value': i, 'label': i} for i in range(min_year, max_year + 2, SLIDER_YEAR_INCREMENT)
        ],
        persistence=True,
        persistence_type='session',
        color='white',
        style={'width': '50%'},
        styles={
            'bar': {'background-color': f'{color}', 'height': '3px'},
            'track': {'height': '3px'},
            'mark': {'display': 'None'},
            'markLabel': {'margin-top': '15px'},
            'thumb': {'background-color': f'{color}', 'border': f'solid 2px {color}'}
        }
    )


@callback(
    Output('average-prevalence-per-country', 'data'),
    Input('year-slider', 'value'),
    State('disorder-data', 'data'),
    prevent_initial_call=True
)
def update_data_on_year(year_range, data):
    """
    Crée un nouveau sous-ensemble à partir des données principales du trouble qui sont filtrées sur une plage d'années spécifique
    """
    df = pd.DataFrame(data)
    filtered_on_year = df.query("@year_range[0] <= Year <= @year_range[1]")
    filtered_on_year_grouped = filtered_on_year.groupby(['Entity', 'Code'])['Value'].mean().reset_index()
    return filtered_on_year_grouped.to_dict('records')


@callback(
    Output('choropleth-container', 'children'),
    Output('choropleth-fig', 'figure', allow_duplicate=True),
    Input('average-prevalence-per-country', 'data'),
    State('select-disorder', 'value'),
    State('choropleth-fig', 'figure'),
    prevent_initial_call=True
)
def update_choropleth_fig(data, disorder_name, figure):
    """
    Met à jour la figure choroplèthe avec les données du trouble filtrées sur une plage d'années spécifique
    """
    data_to_df = pd.DataFrame(data)
    data_to_df['Continent'] = data_to_df['Code'].apply(country_code_to_continent_name)

    if figure:
        color_scale_seq = all_disorders_dataframes[disorder_name].color_scale

        patched_choropleth = Patch()
        patched_choropleth['data'][0]['customdata'] = list(zip(data_to_df['Entity'], data_to_df['Continent']))
        patched_choropleth['data'][0]['locations'] = data_to_df['Code']
        patched_choropleth['data'][0]['z'] = data_to_df['Value']
        patched_choropleth['layout']['coloraxis']['colorscale'] = [
            [i / (len(color_scale_seq) - 1), color] for i, color in enumerate(color_scale_seq)
        ]

        return no_update, patched_choropleth

    return [
        dcc.Graph(
            figure=create_choropleth_fig(
                data_to_df,
                color_scale=all_disorders_dataframes[disorder_name].color_scale
            ),
            config=FIG_CONFIG_WITHOUT_DOWNLOAD,
            id='choropleth-fig',
            className='graph-container',
            # clear_on_unhover=True,
            responsive=True
        ),
        dcc.Interval(id='choropleth-interval', interval=CHOROPLETH_INTERVAL),
    ], no_update


@callback(
    Output('selected-entities', 'data'),
    Output('last-entity-add', 'data'),
    Output('cache-selected-continent', 'data'),
    Output('select-continent', 'value'),
    Input('choropleth-fig', 'clickData'),
    Input('select-continent', 'value'),
    Input('del-last-selected-country', 'n_clicks'),
    Input('del-all-selected-country', 'n_clicks'),
    State('selected-entities', 'data'),
    State('last-entity-add', 'data'),
    State('cache-selected-continent', 'data'),
    State('select-disorder', 'value'),
    prevent_initial_call=True
)
def update_selected_entities(
        choropleth_data,
        selected_continent,
        _1, _2,
        current_entities: dict,
        last_entity: list,
        cache_continent: list,
        disorder_name: str
):
    """
    Met à jour le dcc.Store qui contient la liste de toutes les entités sélectionnées
    """
    input_id = ctx.triggered_id

    # Obtenir le pays sur un clic de la choroplèthe
    if choropleth_data and input_id == 'choropleth-fig':
        new_country, new_continent = get_country_continent_name(choropleth_data)

        if new_continent not in {continent for continent in current_entities}:
            current_entities.update({new_continent: [new_country]})
            update_last_entity(last_entity, new_continent, new_country)
            cache_continent.append(new_continent)
        elif new_country not in current_entities[new_continent]:
            current_entities[new_continent].append(new_country)
            update_last_entity(last_entity, new_continent, new_country)

    elif input_id == 'select-continent':
        difference_cache_and_selected = len(cache_continent) - len(selected_continent)

        # Cas où un continent a été supprimé par l'utilisateur
        if difference_cache_and_selected > 0 and current_entities:
            continent_to_remove = [continent for continent in cache_continent if continent not in selected_continent]

            # Supprimer le continent de current_entities, last_entity et cache_continent:
            del current_entities[continent_to_remove[0]]
            last_entity = [
                [continent, country] for continent, country in last_entity if continent != continent_to_remove[0]
            ]
            cache_continent.remove(continent_to_remove[0])

        else:
            # Ajouter un nouveau continent avec les pays associés
            disorder_df = all_disorders_dataframes[disorder_name].prevalence_by_country

            for continent in selected_continent:
                disorder_df_filtered = disorder_df.query('Continent in @continent')[
                    ['Entity', 'Continent']].drop_duplicates()

                for i, row in enumerate(disorder_df_filtered.iterrows()):
                    continent, country = row[1]['Continent'], row[1]['Entity']

                    if continent not in current_entities:
                        current_entities.update({continent: [country]})
                    else:
                        if country not in current_entities[continent]:
                            current_entities[continent].append(country)

                    update_last_entity(last_entity, continent, country)

                # Mettre à jour le cache avec le nouveau continent:
                _, last_continent, = get_last_added_entity(last_entity)
                if last_continent not in cache_continent:
                    cache_continent.append(last_continent)

    # Supprimer le dernier pays sélectionné ou effacer tous les pays
    elif all((input_id.startswith('del'), current_entities, last_entity)):

        if 'last' in input_id:
            country_to_del, continent_targ = get_last_added_entity(last_entity)

            # Supprimer le dernier pays ajouté:
            current_entities[continent_targ].remove(country_to_del)

            # Vérifier si la clé du continent contient encore des pays, sinon la supprimer :
            if not current_entities[continent_targ]:
                del current_entities[continent_targ]
                cache_continent.remove(continent_targ)

            # Supprimer l'entité supprimée (le dernier élément) de last_entity :
            last_entity.pop()

        else:
            current_entities, last_entity, cache_continent = dict(), list(), list()

    selected_continent = cache_continent

    return current_entities, last_entity, cache_continent, selected_continent


@callback(
    Output('country-title-container', 'children'),
    Output('base-title', 'children'),
    Input('last-entity-add', 'data'),
    prevent_initial_call=True
)
def update_country_title(last_entity: list):
    """
    Met à jour le titre principal en fonction du dernier pays sélectionné par l'utilisateur
    """
    if last_entity:
        last_country, *_ = get_last_added_entity(last_entity)

        return create_country_title(
            last_country,
            'country-title-container',
            'animate__animated animate__flash'
        ), 'Explorer les tendances de santé mentale dans'

    return None, 'Sélectionnez un pays pour explorer les tendances de santé mentale'


@callback(
    Output('choropleth-tooltip', 'label'),
    Output('choropleth-tooltip', 'color'),
    Input('choropleth-fig', 'hoverData'),
    State('select-disorder', 'value'),
    State('year-slider', 'value'),
    prevent_initial_call=True
)
def update_choropleth_tooltip(data, disorder_name, year_range):
    if data:
        (country, continent), prevalence = get_country_continent_name(data), data['points'][0]['z']

        return dmc.Container(
            [
                dmc.Group(
                    [
                        dmc.Text(country, weight=500),
                        DashIconify(
                            icon=f'emojione:flag-for-{country.lower().replace(" ", "-")}',
                            height=20,
                        )
                    ],
                    spacing='xs'
                ),
                dmc.Text(
                    f'Prévalence moyenne des {disorder_name} de {year_range[0]} à {year_range[1]}: '
                    f'{round(prevalence, 2)}%'
                )
            ],
            px=0
        ), 'rgba(11, 6, 81, 0.8)'

    raise PreventUpdate


@callback(
    Output('annual-prevalence-per-country', 'data'),
    Input('selected-entities', 'data'),
    Input('disorder-data', 'data'),
    Input('year-slider', 'value'),
    prevent_initial_call=True
)
def update_annual_prevalence_country(selected_entities, disorder_data, year_range):
    """
    Met à jour les données de prévalence annuelle par pays.
    Ce callback est déclenché lorsque les utilisateurs cliquent sur des pays (carte choroplèthe), éditent l'intervalle d'années (curseur d'années),
    éditent les données de trouble (données de trouble).
    Cela renverra un ensemble de données filtré qui contient tous les pays sélectionnés et qui sera utilisé dans un autre callback
    pour construire les graphiques (carte thermique, sankey).
    """

    if all((selected_entities, disorder_data, year_range)):
        df = pd.DataFrame(disorder_data)
        countries = [country for sublist in selected_entities.values() for country in sublist]
        filtered_df = filter_dataframe(df, countries, year_range, 'Entity')
        return filtered_df.to_dict('records')

    return None


@callback(
    Output('heatmap-container', 'children'),
    Input('annual-prevalence-per-country', 'data'),
    Input('switch-country-continent', 'checked'),
    prevent_initial_call=True
)
def update_heatmap_fig(filtered_data, switch_filter):
    if not filtered_data:
        return update_no_data(
            text='Veuillez choisir des pays en cliquant sur la carte du monde ou ajoutez-les rapidement en sélectionnant un continent dans la liste déroulante'
        )

    filtered_df = pd.DataFrame(filtered_data)
    disorder_name = filtered_df.iloc[0]['Disorder']
    grouping_field = (switch_filter and 'Continent') or 'Entity'  # Column to use when grouping filtered_df

    # Grouping by Continent and Year to compute the Mean per Continent before computing the slope
    if switch_filter:
        filtered_df = filtered_df.groupby(['Continent', 'Year'])['Value'].mean().reset_index()

    slope_by_entity = filtered_df.groupby(grouping_field)['Value'].apply(calculate_slope)
    sorted_entities = slope_by_entity.sort_values(ascending=False).index

    # Data management for plotting heatmap
    df_pivot = filtered_df.pivot(index=grouping_field, columns='Year', values='Value')
    df_normalized = df_pivot.apply(lambda x: (x - x.min()) / (x.max() - x.min()), axis=1).reindex(sorted_entities)

    heatmap_graph_object = add_loading_overlay(
        elements=dcc.Graph(
            figure=create_heatmap(
                df=df_normalized,
                disorder_name=disorder_name,
                entities=sorted_entities,
                grouping_field='Country' if grouping_field == 'Entity' else grouping_field
            ),
            config=FIG_CONFIG_WITH_DOWNLOAD,
            id='heatmap-fig'
        )
    )

    return heatmap_graph_object


@callback(
    Output('sankey-data', 'data'),
    Input('select-disorder', 'value'),
    Input('selected-entities', 'data'),
    Input('year-slider', 'value'),
    Input('switch-age-sex', 'checked'),
    prevent_initial_call=True
)
def update_sankey_data(disorder_name, entities, year_range, switcher):
    all_countries = [country for sublist in entities.values() for country in sublist]

    if not all_countries or (not switcher and disorder_name == 'Eating'):
        return None

    if switcher:
        df_to_use = all_disorders_dataframes[disorder_name].prevalence_by_sex
    else:
        df_to_use = all_disorders_dataframes[disorder_name].prevalence_by_age

    filtered_df = filter_dataframe(
        df=df_to_use,
        entities=all_countries,
        column_to_filter='Entity',
        year_range=year_range
    )

    return filtered_df.to_dict('records')


@callback(
    Output('sankey-container', 'children'),
    Input('sankey-data', 'data'),
    Input('sankey-country-filter-selection', 'value'),
    Input('sankey-year-slider', 'value'),
    State('select-disorder', 'value'),
    State('switch-age-sex', 'checked'),
    State('selected-entities', 'data'),
    prevent_initial_call=True
)
def update_sankey_fig(sankey_data, country_filter_selection, sankey_year, disorder_name, switcher, entities):
    if not sankey_data and not switcher and disorder_name == 'Eating':
        return update_no_data(
            text='Malheureusement, il n\'existe pas de données disponibles sur les catégories d\'âge pour les troubles de l\'alimentation pour le moment'
        )
    if not sankey_data:
        return update_no_data(
            text='Veuillez choisir des pays en cliquant sur la carte du monde ou ajoutez-les rapidement en sélectionnant un continent dans la liste déroulante'
        )

    # Initialize data for Sankey
    filtered_df = pd.DataFrame(sankey_data)
    filtered_df_on_year = filtered_df.query('Year == @sankey_year')
    filtered_categories = [category for category in filtered_df_on_year.columns[3:-1]]

    # Add column with estimated population for each country
    all_countries = [country for item in entities.values() for country in item]
    population_per_country_df = get_population_data(entities=all_countries, year=sankey_year)
    filtered_df_on_year_with_pop = filtered_df_on_year.merge(population_per_country_df, on='Entity', how='inner')
    filtered_df_on_year_with_pop = filtered_df_on_year_with_pop[
        [col for col in filtered_df_on_year_with_pop.columns if not col.endswith('_y')]
    ]
    filtered_df_on_year_with_pop.columns = [col.replace('_x', '') for col in filtered_df_on_year_with_pop.columns]

    # Add column with prevalence global per country
    prevalence_global_country = all_disorders_dataframes[disorder_name].prevalence_by_country
    prevalence_global_country = filter_dataframe(
        df=prevalence_global_country,
        entities=all_countries,
        column_to_filter='Entity',
        year_range=sankey_year
    )
    filtered_df_on_year_with_pop = filtered_df_on_year_with_pop.merge(
        prevalence_global_country, on='Entity', how='inner')
    filtered_df_on_year_with_pop = clean_duplicated_columns(filtered_df_on_year_with_pop)
    filtered_df_on_year_with_pop = filtered_df_on_year_with_pop.rename(columns={'Value': 'GlobalPrevalence'})

    if switcher:
        title = f'Cartographie globale de la prévalence des {disorder_name} par sexe: Du continent au pays'
    else:
        title = f'Flux de prévalence globale des troubles {disorder_name}: Du continent aux groupes d\'âge'

    fig = create_sankey(
        filtered_df_on_year_with_pop,
        filtered_categories=filtered_categories,
        country_filter_selection=country_filter_selection,
        title=title,
        color_categories=['rgb(173, 216, 230)', 'rgb(255, 182, 193)'] if switcher else None
    )

    return add_loading_overlay(dcc.Graph(figure=fig, config=FIG_CONFIG_WITH_DOWNLOAD, id='sankey-fig'))


@callback(
    Output('sankey-year-slider', 'min'),
    Output('sankey-year-slider', 'max'),
    Output('sankey-year-slider', 'value'),
    Output('sankey-year-slider', 'marks'),
    Output('sankey-year-slider', 'disabled'),
    Input('sankey-data', 'data'),
    prevent_initial_call=True
)
def update_sankey_year_slider(sankey_data):
    if sankey_data:
        df = pd.DataFrame(sankey_data)
        min_year, max_year = df['Year'].min(), df['Year'].max()
        thresholds_steps = [(10, 1), (15, 2), (30, 5)]
        range_year = max_year - min_year
        step = next(step for threshold, step in thresholds_steps if range_year <= threshold)

        marks = [
            {'value': i, 'label': i} for i in range(min_year, max_year + 1, step)
        ]

        return min_year, max_year, min_year, marks, False

    else:
        return no_update, no_update, no_update, no_update, True


@callback(
    Output('switch-country-continent', 'disabled'),
    Output('switch-age-sex', 'disabled'),
    Input('selected-entities', 'data'),
    prevent_initial_call=True
)
def update_state_switcher(data):
    if not data:
        return True, True
    return False, False


clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='toggle_modal_heatmap'),
    Output('data-modal-heatmap', 'opened'),
    Input('about-data-management-heatmap', 'n_clicks'),
    State('data-modal-heatmap', 'opened')
)

clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='toggle_modal_sankey'),
    Output('data-modal-sankey', 'opened'),
    Input('about-data-management-sankey', 'n_clicks'),
    State('data-modal-sankey', 'opened')
)

clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='stop_animate_choropleth'),
    Output('choropleth-interval', 'max_intervals'),
    Input('stop-interval', 'n_clicks')
)

clientside_callback(
    """
    function(_, figure) {
        let rotation_lon = figure.layout.geo.projection.rotation.lon;
        let rotation_lat = figure.layout.geo.projection.rotation.lat;

        if (rotation_lon <= -180) {
            rotation_lon = 180;
        }

        if (rotation_lon >= 180) {
            rotation_lon = -180;
        }

        if (rotation_lat >= 90) {
            rotation_lat = 90;
        } else if (rotation_lat <= -90) {
            rotation_lat = -90;
        }

        if (Math.abs(0 - rotation_lat) < 0.01) {
            rotation_lat = 0;
        }

        const updatedFigure = Object.assign({}, figure);
        updatedFigure.layout.geo.projection.rotation.lon = rotation_lon + 0.5;
        updatedFigure.layout.geo.projection.rotation.lat = rotation_lat;

        return updatedFigure;
    }
    """,
    Output('choropleth-fig', 'figure'),
    Input('choropleth-interval', 'n_intervals'),
    State('choropleth-fig', 'figure'),
    prevent_initial_call=True
)
