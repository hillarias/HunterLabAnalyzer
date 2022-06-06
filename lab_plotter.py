import streamlit as st
import pandas as pd
import numpy as np 
import csv
from io import StringIO
from PIL import Image




st.set_page_config(layout="wide")

st.image(image,width=300)
st.title('LAB Color Analyzer') 
st.header('Mean LAB Values')



def lab_analyzer_v2():
    uploaded_file = st.file_uploader("Upload a csv file!", type={"csv", "txt"})
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

table = lab_analyzer_v2()
st.write(table)




if table is not None:
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
        
