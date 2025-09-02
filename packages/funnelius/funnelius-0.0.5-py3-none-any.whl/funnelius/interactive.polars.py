import streamlit as st
import pandas as pd
import polars as pl
import numpy as np
from functions import transform, apply_filter, aggregate, draw, hex_to_rgb, merge_with_compare, add_compare_only_nodes, add_compare_only_edges

compare_file = None
# function used to write a sample python code and jupyter noot book files /////////////////////////////////////////////////
def write_python():
    global csv_file
    global compare_file
    global first_actions_filter
    global goals
    global max_routes
    global show_drop
    global show_answer
    global max_visible_answers
    global gradient
    global gradient_metric
    global metrics

    with open('funnelius_code.py', 'w') as f:
        text = '# import neccessary libraries\n'
        text += 'import pandas as pd\n'
        text += 'import funnelius as fs\n'
        text += '\n#read csv file\n'
        text += 'df = pd.read_csv("'+csv_file.name+'")\n'


        if compare_file is not None:
            text += '\n#read comparison file\n'
            text += 'df_compare = pd.read_csv("'+compare_file.name+'")\n'

        text += '\n# render graph\n'    
        text += 'fs.render(df'

        if compare_file is not None:
            text += ', comparison_df=df_compare'

        text+= ', first_actions_filter=[' + ','.join(first_actions_filter)+']'
        text+= ', goals=[' + ','.join(goals)+']'
        text+= ', max_path_num=' + str(max_routes)
        text+= ', show_drop=' + str(show_drop)
        text+= '\n, show_answer=' + str(show_answer)
        text+= ', max_visible_answers=' + str(max_visible_answers)
        text+= ', gradient=' + '["'+'","'.join(x for x in gradient)+'"]'
        text+= ', gradient_metric="' + gradient_metric+'"'
        text+= '\n, metrics=["' + '","'.join(metrics) + '"]'

        text +=')'
        f.write(text)
        f.close()

# setting initial parameters //////////////////////////////////////////////////////
max_edge_width = 20
first_actions_filter =[]
goals = ['']
min_edge_count = 0
has_compare = 0
gradient_metric = 'conversion-rate'
gradient = ['#fff','#fff','#fff']
gradient_lookup = {
    'Red -> White -> Green':['#ffcdcd','#fff','#cdffcd'],
    'Green - > White -> Red':['#cdffcd','#fff','#ffcdcd'],
    'Red -> White':['#ffcdcd','#ffe6e6','#fff'],
    'White -> Green':['#fff','#e6ffe6','#cdffcd']
}

metric_lookup = {
    'conversion-rate':'Conversion Rate',
    'duration-median':'Duration Median',
    'duration-mean':'Duration Mean',
    'percent-of-total':'% of Total Users',
    'users':'Users'
}


st.sidebar.title('Funnelius')


st.sidebar.subheader("Load Data", divider="gray")
csv_file = st.sidebar.file_uploader("Choose a CSV file", accept_multiple_files=False)
if csv_file is not None:
    raw_data = pl.read_csv(csv_file)


    # compare file //////////////////////////////////////////////////////////////////////////////////
    compare = st.sidebar.checkbox("Compare with another file", value = False)
    if compare == True:
        compare_file = st.sidebar.file_uploader("Choose a CSV file to compare", accept_multiple_files=False)
        if compare_file is not None:
            compare_data = pl.read_csv(compare_file)
            has_compare = 1

    data, first_actions, all_actions = transform(raw_data)
    if has_compare == 1:
        data_compare, __v1, all_actions_compare = transform(compare_data)
    

    st.sidebar.subheader("Filters", divider="gray")
    first_actions_filter = st.sidebar.multiselect(
        "Only paths that start from?",
        first_actions,
        default=[],
    ) 
    goals = st.sidebar.multiselect(
        "Steps that show funnel completion",
        all_actions,
        default=[],
    ) 

    data, route_num =  apply_filter(data, first_actions_filter, goals)
    if has_compare == 1:
        data_compare, route_num_compare = apply_filter(data_compare, first_actions_filter, goals)
        route_num = max(route_num, route_num_compare)
    

    max_routes = st.sidebar.slider('Maximum paths to show', min_value=1, max_value=route_num, value=route_num, key="route_slider")

    # show percentage of sampling based on maximum routes selected
    if max_routes < route_num:
        all_route_users = len(data.select(pl.col("user_id").unique()))
        sampled_route_users = len(data.filter(pl.col("route_order") <= max_routes).select(pl.col("user_id").unique()))
        st.sidebar.text(str(int(sampled_route_users/all_route_users*100))+'% of data')

    show_answer = st.sidebar.checkbox("Show Answer contribution", value = False)
    if show_answer == True:
        max_visible_answers = st.sidebar.slider('Maximum Visible Answers', min_value=1, max_value=20, value=5) 
    else:
        max_visible_answers = 5 
 
    data_node, data_edge, data_answer = aggregate(data, max_routes, max_visible_answers)
    if has_compare == 1:
        data_compare_node, data_compare_edge, data_compare_answer = aggregate(data_compare, max_routes, max_visible_answers)


        #add compare data to original data   
        
        #merge data with compare_data
        merge_with_compare(data_node,data_compare_node,data_edge,data_compare_edge,data_answer,data_compare_answer)
        
        #calculate increase/decrease percentages for nodes
        metrics = ['conversion_rate','duration_median','duration_mean','percent_of_total','users']
        for metric in metrics:
            data_node[metric+'_change'] = data_node[metric]/data_node[metric+'_compare'] - 1

        #calculate increase/decrease percentages for answers
        data_answer['answer_percent_change'] = data_answer['answer_percent']/data_answer['answer_percent_compare'] - 1

        #calculate increase/decrease percentages for edges
        data_edge['edge_count_change'] = data_edge['edge_count']/data_edge['edge_count_compare'] - 1
        
        #add nodes that were present in comparison data but not in original data
        data_node = add_compare_only_nodes(data_node, data_compare_node)    

        #add edges that were present in comparison data but not in original data
        data_edge = add_compare_only_edges(data_edge, data_compare_edge)


    metrics = st.sidebar.pills('Metrics to show', ['users','conversion-rate','percent-of-total','duration-median', 'duration-mean'], selection_mode = 'multi', 
    default = ['users','conversion-rate','percent-of-total','duration-median'], format_func = lambda option: metric_lookup[option])
    
    show_drop = st.sidebar.checkbox("Show drops", value = True)

    general_file_name = csv_file.name.split('.')[0]

    
    # Conditional formating settings///////////////////////////////////////////////////////////////
    st.sidebar.subheader("Conditional Formatting", divider="gray")
    with st.sidebar.expander("See explanation"):
        conditional = st.sidebar.checkbox("Apply Conditional Formatting", value = False)
        if conditional == True:
            gradient = st.sidebar.selectbox('Gradient Color', ('Red -> White -> Green', 'Green - > White -> Red',  'Red -> White', 'White -> Green'))
            gradient = gradient_lookup[gradient]
            
            rgb_list = hex_to_rgb(gradient)
            html = '<div width="100%" style="background: #FFDCDC;background: linear-gradient(90deg'
            for i in range(0,3):
                html += ',rgba('
                html += ', '.join(str(rgb_list[i][j]) for j in range(0,3))
                html += ', 1) '+str(i*50)+'%'
            html += ');"> &nbsp;</div>'

            st.sidebar.html(html)
            gradient_metric = st.sidebar.selectbox('Metric', ('conversion-rate', 'duration-median', 'duration-mean', 'percent-of-total', 'users'), format_func = lambda option: metric_lookup[option] )
      
    # Draw chart and load it into sttreamlit //////////////////////////////////////
    draw(data_node, data_edge, data_answer, goals, min_edge_count, max_edge_width, general_file_name, show_drop, show_answer, max_visible_answers , ['svg','pdf'], gradient, gradient_metric, metrics = metrics)
    st.image(general_file_name+'.svg',width=1000)

    #export part of sidebar///////////////////////////////////////////////////////////////
    st.sidebar.subheader("Export", divider="gray")
    with open(general_file_name+'.pdf', 'rb') as file:
        st.sidebar.download_button(
            label='Download PDF',
            data=file,
            file_name=general_file_name+'.pdf',
            mime='image/pdf',
            icon=':material/download:',
        )
    write_python()
    with open('funnelius_code.py', 'rb') as code_file:
        st.sidebar.download_button(
            label='Download Python Code',
            data=code_file,
            file_name='funnelius_code.py',
            mime='text/x-python',
            icon=':material/download:',
        )

else:
    st.info('Please load a csv file from left sidebar.', icon="ℹ️")



