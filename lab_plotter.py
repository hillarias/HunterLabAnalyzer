import streamlit as st
import pandas as pd
import numpy as np 
import csv
import plotly.express as px
import plotly as pl
from io import StringIO
from PIL import Image
import plotly.graph_objects as go
import skimage
from pyciede2000 import ciede2000





st.set_page_config(layout="wide")


st.title('LAB Color Analyzer') 
st.header('Mean LAB Values')

uploaded_file = st.file_uploader("Upload a csv file!", type={"csv", "txt"})

def lab_analyzer_mean(uploaded_file):
    
    if uploaded_file is not None:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        read_file = csv.reader(stringio, delimiter=",")
        data = list(read_file)
        
        
        #removes unnecessary header from csv,always first 13 cells#
        no_header = data[13:]
        
        
        #removeing all spectral data that is not lab values
        no_sides = []

        for row in range(len(no_header)):
            try:
                if len(no_header[row][0]) == 0:
                    break
                current_row = []
                for col in range(5):
                    current_row.append(no_header[row][col])
                no_sides.append(current_row)
            
            except IndexError:
                break

        
        
        table = pd.DataFrame(no_sides,  dtype = float)

        new_header = table.iloc[0] #grab the first row for the header
        table = table[1:] #take the data less the header row
        table.columns = new_header #set the header row as the df header

        df = table.loc[: , ['Name','L*','a*','b*'] ] 
        
        
        #removing _1,_2,_3..etc. from replicated experimental groups##
        iterations = 10
        for i in range(1, iterations +1):
            df['Name'] = df['Name'].str.replace('_'+str(i),'')
        
        ##removing all underscores for appearance##
        df['Name'] = df["Name"].str.replace('_',' ')
        
        ##setting index to experiment name and changing object type columns to float
        df2 = df.set_index(['Name'])
        df2["L*"] = pd.to_numeric(df2["L*"], downcast="float")
        df2["a*"] = pd.to_numeric(df2["a*"], downcast="float")
        df2["b*"] = pd.to_numeric(df2["b*"], downcast="float")
        
        ##grouping and rounding to 3 decimal places##
        df_grouped = df2.groupby(['Name']).mean()
        l_star = np.round(list(df_grouped["L*"]) , 3)
        a_star = np.round(list(df_grouped["a*"]) , 3)
        b_star = np.round(list(df_grouped["b*"]) , 3)
        
        df_grouped["L*"] = l_star
        df_grouped["a*"] = a_star
        df_grouped["b*"] = b_star

        
            
        return df_grouped

if uploaded_file is not None:
    table = lab_analyzer_mean(uploaded_file)
    st.write(table)

    fig = px.scatter_3d(table, x='a*', y='b*', z='L*',color= table.index)
        
    fig.update_layout(scene = dict(
                        xaxis_title='a*',
                        yaxis_title='b*',
                        zaxis_title='L*'),
                        width=600,
                        height = 600
                            
                    )
            
    ##Makes axes cube 
    fig.update_layout(scene_aspectmode='cube')
            
    fig.update_layout( title = 'LAB Values' , title_x = 0.45 , title_y = .90 , legend_font_size= 15 )
            
            
            


    #st.write(lab_plotter_no_labels_no_hex(table,'test'))
    st.header('Mean LAB Values - 3D Plot')
    st.plotly_chart(fig, sharing="streamlit" , use_container_width=True)
        

def lab_analyzer_std(uploaded_file):

    if uploaded_file is not None:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        read_file = csv.reader(stringio, delimiter=",")
        data = list(read_file)
    
    #removes unnecessary header from csv,always first 13 cells#
    no_header = data[13:]
    
    
    #removeing all spectral data that is not lab values
    no_sides = []

    for row in range(len(no_header)):
        try:
            if len(no_header[row][0]) == 0:
                break
            current_row = []
            for col in range(5):
                current_row.append(no_header[row][col])
            no_sides.append(current_row)
        
        except IndexError:
            break

    
    
    table = pd.DataFrame(no_sides,  dtype = float)

    new_header = table.iloc[0] #grab the first row for the header
    table = table[1:] #take the data less the header row
    table.columns = new_header #set the header row as the df header

    df = table.loc[: , ['Name','L*','a*','b*'] ] 
    
    
    #removing _1,_2,_3..etc. from replicated experimental groups##
    iterations = 10
    for i in range(1, iterations +1):
        df['Name'] = df['Name'].str.replace('_'+str(i),'')
    
    ##removing all underscores for appearance##
    df['Name'] = df["Name"].str.replace('_',' ')
    
    ##setting index to experiment name and changing object type columns to float
    df2 = df.set_index(['Name'])
    df2["L*"] = pd.to_numeric(df2["L*"], downcast="float")
    df2["a*"] = pd.to_numeric(df2["a*"], downcast="float")
    df2["b*"] = pd.to_numeric(df2["b*"], downcast="float")
    
    ##grouping and rounding to 3 decimal places##
    df_grouped = df2.groupby(['Name']).std()
    l_star = np.round(list(df_grouped["L*"]) , 3)
    a_star = np.round(list(df_grouped["a*"]) , 3)
    b_star = np.round(list(df_grouped["b*"]) , 3)
    
    df_grouped["L*"] = l_star
    df_grouped["a*"] = a_star
    df_grouped["b*"] = b_star
    
    name_dictionary = {'L*': 'L*STD','a*':'a*STD', 'b*':'b*STD'}
    
    df_grouped = df_grouped.rename(columns= name_dictionary)

    return df_grouped

def lab_analyzer_v3(filename):
    average_vals = lab_analyzer_mean(filename)
    std_vals = lab_analyzer_std(filename)
    std_vals.drop(average_vals.index)
    df_add =  pd.concat([average_vals, std_vals], axis=1)
    
    return df_add


def lab_bar_plotter(filename):
    table = lab_analyzer_v3(filename)
    
    fig = go.Figure()

    fig.add_bar(x= table.index , y= table['L*'] , name = 'L*', error_y  = 
                                                                   dict( type = 'data',
                                                                    array = table['L*STD'],
                                                                    visible = True),
                                                                    marker_color = 'SlateGray'
                                                                    
                                                                   )
    fig.add_bar(x= table.index , y= table['a*'], name = 'a*', error_y  = 
                                                                   dict( type = 'data',
                                                                    array = table['a*STD'],
                                                                    visible = True),
                                                                    marker_color = 'IndianRed'
                                                                   )
    fig.add_bar(x= table.index , y= table['b*'] , name = 'b*', error_y  = 
                                                                   dict( type = 'data',
                                                                    array = table['b*STD'],
                                                                    visible = True),
                                                                       marker_color = 'Gold'
                                                                   )
    fig.update_layout( title = 'LAB Values' , title_x = 0.45 , title_y = .90 , legend_font_size= 15 )
    return fig


def lab_to_rgb(df):
    
##creating 3 lists corresponding to l a b    ## 
    l_lst  = df['L*'].tolist()
    a_lst = df['a*'].tolist()
    b_lst = df['b*'].tolist()

    
##nested list of lab values##
    combined_lab = []
    for i in range(len(l_lst)):
        combined_lab += [ [l_lst[i]] + [a_lst[i]] + [b_lst[i]]  ]
        
##Numpy array for use in skimage package, skimage used to convert lab to rgb, turned to list for further modifi.##        
    
    lab_array = np.array(combined_lab)

    rgb_lst  = skimage.color.lab2rgb(combined_lab).round(4).tolist()


##tuple transformation, matplotlib.colors.to.hex  needs tuple format.##
    
    nested_lst_of_tuples =  [tuple(i) for i in rgb_lst]

    rgb_tup  =  tuple(nested_lst_of_tuples)
    

    rgb_format = []

    for i in range(len(rgb_tup)):
        temp = [pl.colors.label_rgb(rgb_tup[i])]
        rgb_format += temp
    
    return rgb_format



full_data = (lab_analyzer_v3(uploaded_file))
if full_data is not None:
    st.header('LAB Data')
    st.write(full_data)

    st.header('Mean LAB Data With Standard Deviations Plot')
    st.write(lab_bar_plotter(uploaded_file))

        
    color_swatch = px.bar(full_data, x = full_data.index  , color_discrete_sequence = [lab_to_rgb(full_data)])
    color_swatch.update_layout(barmode='group', bargap=0,bargroupgap=0.0)
    st.write(color_swatch)     
        
        
def de2000_calculator(df, reference_lab):
    
    ##creating 3 lists corresponding to l a b    ## 
    l_lst  = df['L*'].tolist()
    a_lst = df['a*'].tolist()
    b_lst = df['b*'].tolist()

    
##nested list of lab values##
    combined_lab = []
    for i in range(len(l_lst)):
        combined_lab += [ [l_lst[i]] + [a_lst[i]] + [b_lst[i]]  ]
        
    nested_lst_of_tuples =  [tuple(i) for i in combined_lab]

    lab_tup  =  tuple(nested_lst_of_tuples)    
    
    
    de2000_lst = []
    
    for i in range(len(lab_tup)):
        
        res = ciede2000(lab_tup[i] , reference_lab)
        
        temp_val = res['delta_E_00']
        
        de2000_lst += [temp_val]   

    return de2000_lst

st.header('ΔE2000 From Reference Point')
l_star = float(st.text_input('Type a reference L*'))
a_star = float(st.text_input('Type a reference a*'))
b_star = float(st.text_input('Type a reference b*'))
ref_name = st.text_input('Type the name of the reference!')

ref_col_name = 'ΔE00'+ "-" + ref_name
ref_lab = tuple([l_star,a_star,b_star]) 
    
if ref_name is not None:
        de00_vals = de2000_calculator(table, ref_lab)
        
        table[ref_col_name] = de00_vals
        st.subheader('ΔE2000 from ' + ref_name)
        de_scatter = px.scatter(table, x = table.index , y = table.columns[-1])
        st.write(table)
        st.write(de_scatter)
        
