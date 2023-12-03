import pandas as pd
import plotly.express as px
import streamlit as st
import nomiden
from nomiden import reader as nr

st.set_page_config(layout = "wide")

cust = pd.read_csv("customer_all.csv")
coord = pd.read_csv('data/coordinate.csv')

nik_generate = pd.DataFrame(cust['NIK'].apply(lambda x: nr.NIK(x).all_info).to_list())
gab = cust.merge(right = nik_generate,
                on = "NIK")
gab[["CustomerID","NIK"]] = gab[["CustomerID","NIK"]].astype("object")
gab[["Profession"]] = gab[["Profession"]].astype("category")
gab["birth_year"] = gab['birth_datetime'].dt.year

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customer", gab.shape[0])
col2.metric("Male", gab['gender'].value_counts()[0])
col3.metric("Female", gab['gender'].value_counts()[1])
col4.metric("Age", f"{gab['age'].min()} to {gab['age'].max()}")

st.divider()

st.title("Customer Analysis")
st.write("Here we want to know our customer segmentation from their job or where they lives. You can access the data and the source code from my [GitHub](https://github.com/rahmarania).")
st.write("Build and modified by Rahma Fairuz Rania")

st.divider()

col5, col6 = st.columns(2)

# slider 1
input_slider = col5.slider(label = "Number of Bar", min_value = 0, max_value = 10)

# plot 1
col5.write("### Customer Profession by Gender") 
job_dist = pd.crosstab(index = gab["Profession"],
            columns = gab["gender"],
            colnames = [None]).melt(ignore_index= False, var_name = "gender", value_name = 'total').reset_index().sort_values(by = "Profession").head(input_slider)
fig1 = px.bar(job_dist, y="Profession", x="total", color="gender", barmode="group")
col5.plotly_chart(fig1, use_container_width = True)

# plot 2
col6.write("### Customer's Annualy Income") 
scat_prof_annual = pd.crosstab(index = gab['Profession'],
                               columns = gab['Annual_Income'],
                               colnames=[None]).melt(ignore_index=False, var_name = "income").reset_index()#.sort_values(by = ["Profession","income","value"], ascending = False)
fig2 = px.bar(scat_prof_annual, x="Profession", y="value", color="income",
              hover_data = {'Profession':True, 'income':True, 'value' : False})
col6.plotly_chart(fig2, use_container_width = True)
col6.write("From bar chart above, we can conclude that artist has the highest customer annual income. Total customers who the profession being an Artist is 355 people, which it is 32% of total customers")

st.divider()

# plot 3
options = st.multiselect(label="Select Profession", options=gab['Profession'].unique().tolist())
age_avg = gab[gab['Profession'].isin(options)]
df_avg = age_avg.groupby('Profession')['age'].mean().reset_index(name='Average_Age').sort_values(by = 'Average_Age')
fig3 = px.bar(df_avg, x='Average_Age', y='Profession', orientation='h', 
             title='Average Age by Profession', labels={'Average_Age': 'Average Age'})
col7, col8 = st.columns(2)
col7.plotly_chart(fig3)
col8.write("")
col8.write("As we can see on the graph, customer with Healthcare profession has the highest average of age, and other field also has itself average age. This information would be help business to consider the market strategy, product development, pricing product, offers, etc for better services to our customer")

# plot 4
st.write("### Customers spread accross Indonesia")
spread = pd.crosstab(index = [gab["province"], gab["district"]],
            columns= 'total',
            colnames = [None]).reset_index()
df_map = spread.merge(coord, on = 'province')
plot_map = px.scatter_mapbox(data_frame=df_map, lat='latitude', lon='longitude',
                             mapbox_style='open-street-map', zoom=3,
                             size='total',
                             hover_name='province',
                             hover_data={'district' : True,
                                         'latitude': False,
                                         'longitude': False})
st.plotly_chart(plot_map, use_container_width = True)
