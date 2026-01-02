import streamlit as st
import gspread
import matplotlib.pyplot as plt
from datetime import datetime
from google.oauth2.service_account import Credentials
from tenacity import retry, stop_after_attempt, wait_exponential
@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)

def save_data(worksheet, data):
    worksheet.append_row(data)


# Достаточно составить списки qualities и sports. Формирование web-страницы произойдёт автоматически

qualities = ['Сила воли', 'Выносливость', 'Физическая сила', 'Высокий рост', 'Прыгучесть', 'Гибкость тела', 'Координация движений, ловкость', 'Быстрая реакция', 'Вестибулярная устойчивость', 'Стремление к творчеству и самовыражению', 'Жажда риска', 'Скорость принятия решений', 'Способность выдержать однообразие и монотонность', 'Стойкость, терпение, умение вынести моральные и физические нагрузки', 'Умение планировать и распределять силы', 'Упорство и упрямство', 'Стремление доминировать, возвыситься над людьми', 'Способность к лидерству, умение повести за собой людей', 'Умение подчинять себя интересам коллектива', 'Коммуникабельность', 'Наблюдательность, умение подмечать детали', 'Уважение к окружающим, способность воспринимать чужое мнение', 'Импульсивность, кураж, стремление достичь невозможного', 'Устойчивость к быстро меняющимся ситуациям, умение собраться в критический момент']

sports = ['Футбол', 'Баскетбол', 'Волейбол', 'Гандбол', 'Хоккей', 'Фигурное катание', 'Конькобежный спорт', 'Лыжные гонки', 'Биатлон', 'Горнолыжный спорт', 'Фристайл на роликовых коньках', 'Бег на короткие дистанции', 'Бег на длинные дистанции', 'Лёгкая атлетика многоборье', 'Спортивное ориентирование', 'Спортивная гимнастика', 'Художественная гимнастика', 'Спортивная аэробика', 'Плавание', 'Водное поло', 'Гребля на байдарках', 'Парусный спорт', 'Велоспорт', 'Большой теннис', 'Настольный теннис', 'Бадминтон', 'Дартс', 'Гольф', 'Шахматы', 'Шашки', 'Гиревой спорт', 'Пауэрлифтинг', 'Тяжёлая атлетика', 'Вольная борьба', 'Греко-римская борьба', 'Дзю-до', 'Каратэ', 'Самбо', 'Бокс', 'Таэквондо', 'MMA', 'Стрельба из винтовки', 'Стрельба из пистолета', 'Стрельба из лука', 'Фехтование', 'Конный спорт']

# Переменные ps, qs, ks, содержащие информацию пользователя, предназначены для заполнения соответствующих полей базы данных

qlen = len(qualities)
qkeys = []
for i in range(0, qlen): qkeys.append("q" + str(i))

slen = len(sports)
ks = "0"*slen
c = []; k = []
for i in range(0, slen): c.append("k" + str(i));k.append(sports[i])

# --------------------------------------------------------

st.title('Спортивная анкета')

st.header('Опрос')

st.text_input('Ваши имя, фамилия и номер группы', key='person')

st.subheader('Оцените Ваши качества')

st.markdown(
    """
    <style>
    .stSlider {
        width: 300px; /* Ширина для смартфонов */
        margin-bottom: 50px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

for i in range(0, qlen):
    st.slider(qualities[i], min_value=0, max_value=10, key=qkeys[i])

st.write('----------------------------------------------')

st.subheader('В каком виде спорта Вы имеете наибольший успех?')

st.markdown(f"И выполняется <b><i><mark>какое-либо</mark></i></b> из условий: <b>регулярные занятия, призовые места на соревнованиях, спортивный разряд</b>...", unsafe_allow_html=True)

for i in range(0, slen): st.checkbox(k[i], key=c[i])

st.write('----------------------------------------------')

savetoDB = st.button('Записать')

def clear_inputs(sk = qkeys, ck = c):
    st.session_state.person = ""
    for qkey in sk: st.session_state[qkey] = 0
    for ckey in ck: st.session_state[ckey] = False

clear = st.button('Очистить', on_click=clear_inputs)

if savetoDB:
    
    ps = st.session_state['person']
    
    qn = []
    qs = ''
    for i in range(0, qlen):
        n = st.session_state[qkeys[i]]
        qn.append(n)
        qs = qs + str(n) + ","
    qs = qs[:-1]
        
    for i in range(0, len(c)):
        if st.session_state[c[i]]: ks = ks[:i] + "1" + ks[(i+1):]

    
    google_creds = st.secrets["gcp_service_account"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(google_creds, scopes=scopes)
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key('1iJ67Z6OrtmK2klJ9ZmXMMQ-HjGvAnRmI6Z-oZ5QSz38')
    ws = sh.get_worksheet(0)
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    nr = [ts, ps, qs, ks]
   
    try:
        save_data(ws, nr)
        st.write(' ')
        st.write('Данные успешно сохранены')
        st.write(ts)
        st.write(' ')
    except Exception as e:
        st.write(' ')
        st.write('Не удалось подключиться к базе данных: ')
        st.write(e)
        st.write(' ')

    
    st.write('----------------------------------------------')

    st.markdown(f"{'&nbsp;' * 8} <b>Характеристика для {ps}</b>", unsafe_allow_html=True)
    st.markdown(f"{'&nbsp;' * 8} Вектор качеств: ({qs})", unsafe_allow_html=True)
    qidx = []
    for i in range(0, qlen): qidx.append(i)
    fig = plt.figure()
    plt.bar(qidx, qn)
    plt.xlim(-1, qlen)
    plt.ylim(0, 10)
    plt.axis('off')
    st.pyplot(fig)


