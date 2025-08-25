import streamlit as st
import google.generativeai as genai
import os

# --- تنظیمات اولیه صفحه ---
st.set_page_config(
    page_title="تست شخصیت هوش مصنوعی 🤖",
    page_icon="🤖",
    layout="centered"
)

# --- سایدبار برای تنظیمات ---
st.sidebar.header("تنظیمات شخصیت ربات")

# دریافت کلید API از کاربر در سایدبار
# برای امنیت بیشتر، بهتر است از متغیرهای محیطی یا st.secrets استفاده شود.
# اما برای سادگی تست، ورودی مستقیم قرار داده شده است.
api_key = st.sidebar.text_input("کلید API Gemini خود را وارد کنید:", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        st.sidebar.error(f"خطا در تنظیم API: {e}")


# متن نمونه برای پرامپت سیستمی (مغز ربات)
DEFAULT_SYSTEM_PROMPT = """
تو مدیر و پاسخگوی مشتریان در دایرکت اینستاگرام یک آتلیه لباس زنانه به نام 'آتلیه رز' هستی. 
شخصیت تو بسیار دوستانه، صبور و شیک است. همیشه از ایموجی‌های مناسب مانند ✨ و 💖 استفاده کن.
تمام دانش تو درباره محصولات و قوانین در ادامه آمده است:

--- لیست محصولات ---
- مانتو مدل بهار: جنس کرپ، قیمت ۱،۵۰۰،۰۰۰ تومان، رنگ‌ها: مشکی، کرم. سایزبندی: ۳۶ تا ۴۴.
- شومیز مدل نسترن: جنس حریر، قیمت ۸۰۰،۰۰۰ تومان، رنگ‌ها: سفید، صورتی. سایزبندی: فری سایز.

--- سوالات متداول ---
- ارسال: ارسال به تهران ۱ روزه با پیک، به شهرستان‌ها ۳ روزه با پست پیشتاز. هزینه ارسال ۳۵ هزار تومان.
- تعویض: تا ۲۴ ساعت پس از تحویل، در صورت عدم استفاده، امکان تعویض سایز وجود دارد.

--- وظیفه تو ---
حالا با استفاده دقیق از این اطلاعات و حفظ شخصیت برند، به پیام‌های مشتریان پاسخ بده.
هرگز اطلاعاتی خارج از این چارچوب ارائه نده.
"""

system_prompt = st.sidebar.text_area(
    "دستورالعمل اصلی (System Prompt):", 
    value=DEFAULT_SYSTEM_PROMPT, 
    height=400
)

# دکمه شروع مجدد چت در سایدبار
if st.sidebar.button("شروع مجدد گفتگو"):
    st.session_state.messages = []


# --- پنجره اصلی چت ---
st.title("🤖 شبیه‌ساز چت با مشتری")
st.write("در اینجا می‌توانید با هوش مصنوعی خود صحبت کنید و عملکرد آن را بر اساس دستورالعمل‌های سایدبار بسنجید.")

# اگر کلید API وارد نشده بود، پیام راهنما نمایش بده
if not api_key:
    st.info("لطفاً برای شروع، کلید API Gemini خود را در سایدبار وارد کنید.")
    st.stop()


# مقداردهی اولیه تاریخچه چت در session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

# نمایش پیام‌های قبلی
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# دریافت ورودی از کاربر
if user_prompt := st.chat_input("شما (در نقش مشتری):"):
    # اضافه کردن پیام کاربر به تاریخچه و نمایش آن
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # ساخت مدل با پرامپت سیستمی
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash-latest',
        system_instruction=system_prompt
    )

    # ساخت تاریخچه برای ارسال به API (بدون پرامپت سیستمی)
    chat_history_for_api = [{"role": msg["role"], "parts": [msg["content"]]} for msg in st.session_state.messages]
    
    # نمایش حالت لودینگ و ارسال درخواست به Gemini
    with st.spinner("هوش مصنوعی در حال فکر کردن است..."):
        try:
            response = model.generate_content(chat_history_for_api)
            ai_response = response.text
            
            # اضافه کردن پاسخ ربات به تاریخچه و نمایش آن
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            with st.chat_message("assistant"):
                st.markdown(ai_response)

        except Exception as e:
            st.error(f"خطایی در ارتباط با Gemini رخ داد: {e}")