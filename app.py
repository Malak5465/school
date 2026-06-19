import streamlit as st
import pandas as pd
from supabase import create_client, Client

# إعدادات الصفحة الأساسية لتناسب الجوال والكمبيوتر
st.set_page_config(
    page_title="برنامج تقييم الأطفال",
    page_icon="👶",
    layout="centered"
)

# ----------------------------------------------------
# ⚙️ إعدادات الربط بـ Supabase (بياناتكِ الحقيقية مفعلة)
# ----------------------------------------------------
SUPABASE_URL = "https://wuozdbisjktrtxarfztq.supabase.co"
SUPABASE_KEY = "sb_publishable_GWhRuvE8hwV2ACeegoG2cw_1J7sd0S2"

# الاتصال التلقائي بقاعدة البيانات السحابية
@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_supabase()
except Exception as e:
    st.error("❌ تعذر الاتصال بـ Supabase. يرجى التأكد من صحة الرابط والمفتاح المكتوبين في الكود.")

# ----------------------------------------------------
# الواجهة الترحيبية للتطبيق
# ----------------------------------------------------
st.markdown("<h1 style='text-align: center; color: #4A90E2;'>🌟 برنامج تقييم الأطفال اليومي 🌟</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #777;'>أهلاً بكِ يا أستاذة ملاك. بياناتكِ الآن تُحفظ تلقائياً في السحاب الآمن.</p>", unsafe_allow_html=True)
st.write("---")

# إنشاء التبويبات الثلاثة الرئيسية
tab1, tab2, tab3 = st.tabs(["➕ إدارة الطالبات", "📝 رصد التقييم اليومي", "🎓 الشهادات والنتائج"])

# ----------------------------------------------------
# التبويب الأول: إدارة الطالبات
# ----------------------------------------------------
with tab1:
    st.subheader("👧 إضافة طفلة جديدة للفصل")
    new_student = st.text_input("أدخلي اسم الطفلة كاملاً:")
    
    if st.button("إضافة الطفلة"):
        if new_student.strip() != "":
            student_name_clean = new_student.strip()
            try:
                check_exist = supabase.table("students").select("*").eq("name", student_name_clean).execute()
                
                if check_exist.data:
                    st.warning("⚠️ هذه الطفلة مضافة بالفعل في الفصل.")
                else:
                    supabase.table("students").insert({"name": student_name_clean}).execute()
                    st.success(f"✅ تم حفظ الطفلة ({student_name_clean}) في قاعدة البيانات بنجاح!")
            except Exception as e:
                st.error(f"حدث خطأ أثناء الحفظ السحابي: {e}")
        else:
            st.error("❌ الرجاء كتابة اسم الطفلة أولاً.")

# جلب قائمة أسماء الفصل من سوبابيس
try:
    db_students = supabase.table("students").select("name").execute()
    students_list = [row["name"] for row in db_students.data] if db_students.data else []
except Exception:
    students_list = []

# ----------------------------------------------------
# التبويب الثاني: رصد التقييم اليومي
# ----------------------------------------------------
with tab2:
    st.subheader("✍️ رصد درجات اليوم")
    
    if not students_list:
        st.info("💡 قائمة الفصل فارغة حالياً. الرجاء إضافة طالبات من التبويب الأول أولاً.")
    else:
        selected_student = st.selectbox("اكتبي أو اختاري اسم الطفلة:", students_list)
        selected_day = st.radio("تحديد اليوم:", ["اليوم الأول", "اليوم الثاني"], horizontal=True)
        
        st.write("---")
        st.markdown("#### 🌟 معايير التقييم (من 1 إلى 5 نجوم):")
        
        behavior = st.slider("⭐ السلوك المتميز:", 1, 5, 5)
        hygiene = st.slider("⭐ النظافة والترتيب:", 1, 5, 5)
        participation = st.slider("⭐ المشاركة والتفاعل:", 1, 5, 5)
        activities = st.slider("⭐ حل الأنشطة والمهام:", 1, 5, 5)
        
        st.write("---")
        
        if st.button("حفظ التقييم السحابي"):
            day_total = behavior + hygiene + participation + activities
            try:
                eval_data = {
                    "student_name": selected_student,
                    "day_number": selected_day,
                    "behavior": behavior,
                    "hygiene": hygiene,
                    "participation": participation,
                    "activities": activities,
                    "total": day_total
                }
                supabase.table("evaluations").insert(eval_data).execute()
                st.success(f"🎉 تم رصد تقييم {selected_student} لـ ({selected_day}) بنجاح! المجموع: {day_total}/20")
            except Exception as e:
                st.error(f"فشل إرسال التقييم: {e}")

# ----------------------------------------------------
# التبويب الثالث: الشهادات والنتائج وقراءة سوبابيس
# ----------------------------------------------------
with tab3:
    st.subheader("🏆 لوحة التحكم والشهادات التلقائية")
    
    try:
        db_evaluations = supabase.table("evaluations").select("*").execute()
        eval_records = db_evaluations.data if db_evaluations.data else []
    except Exception:
        eval_records = []
        
    if not eval_records:
        st.info("💡 لم يتم حفظ أي تقييمات في سوبابيس بعد.")
    else:
        df = pd.DataFrame(eval_records)
        st.dataframe(df[["student_name", "day_number", "total"]], use_container_width=True)
        
        st.write("---")
        st.markdown("#### 📜 إصدار الشهادات:")
        
        student_to_certify = st.selectbox("اختار الطالبة لإصدار الشهادة:", list(set(df["student_name"])))
        
        student_rows = df[df["student_name"] == student_to_certify]
        final_score = int(student_rows["total"].sum())
        
        st.metric(label=f"المجموع الإجمالي لـ {student_to_certify} (من 40 درجة):", value=f"{final_score} / 40")
        
        # تحديد الألقاب والألوان بناءً على الدرجة
        if final_score == 40:
            title = "نجم الأسبوع الخارق 👑"
            bg_color = "#FFFDF0"
            border_color = "#D4AF37"
            title_color = "#D4AF37"
        elif final_score >= 32:
            title = "البطل المتميز ✨"
            bg_color = "#F4F9FF"
            border_color = "#4A90E2"
            title_color = "#4A90E2"
        else:
            title = "البطل المجتهد 👍"
            bg_color = "#FBFBFB"
            border_color = "#A0A0A0"
            title_color = "#7F8C8D"
            
        if final_score == 40:
            st.balloons()
            st.success(f"🏆 اللقب المستحق تلقائياً: **{title}**")
        elif final_score >= 32:
            st.info(f"🌟 اللقب المستحق تلقائياً: **{title}**")
        else:
            st.warning(f"👍 اللقب المستحق تلقائياً: **{title}** (بحاجة لبعض التحسين)")
            
        # زر توليد الشهادة الفعلي داخل التطبيق
        if st.button("🖨️ توليد شهادة نظيفة جاهزة للطباعة"):
            
            # قالب التصميم الجديد والآمن لمنع اللخابيط والرموز
            html_template = """
            <div id="cert-print-area" style="
                border: 10px double __BORDER__;
                padding: 35px;
                text-align: center;
                background-color: __BG__;
                font-family: 'Arial', sans-serif;
                direction: rtl;
                border-radius: 15px;
                margin-top: 25px;
                box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
            ">
                <h1 style="color: __TCOLOR__; margin-bottom: 5px; font-size: 32px;">📜 شهادة تميز وتقدير 📜</h1>
                <p style="font-size: 18px; color: #555; margin-top: 10px;">تتقدم الأستاذة <strong style="color: #333;">ملاك</strong> بكل فخر واعتزاز بمنح هذه الشهادة للطفل/ة:</p>
                
                <h2 style="color: #2C3E50; font-size: 34px; margin: 20px 0; border-bottom: 3px dashed __BORDER__; display: inline-block; padding: 0 40px; font-weight: bold;">
                    __NAME__
                </h2>
                
                <p style="font-size: 18px; color: #555;">وذلك لتألقه/ا الملحوظ في الفصل وتحقيق لقب:</p>
                <h3 style="color: #E74C3C; font-size: 28px; margin: 15px 0; font-weight: bold;">🌟 __TITLE__ 🌟</h3>
                
                <p style="font-size: 16px; color: #7F8C8D; margin-top: 20px;">
                    بمجموع درجات: <strong style="color: #27AE60; font-size: 22px;">__SCORE__ من 40</strong> في التقييم اليومي المتميز.
                </p>
                
                <div style="margin-top: 40px; font-size: 16px; color: #555; text-align: left; padding-left: 20px;">
                    <span>مع تحيات: <strong>أستاذة ملاك 🌸</strong></span>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 25px;">
                <button onclick="window.print()" style="
                    background-color: #27AE60;
                    color: white;
                    border: none;
                    padding: 12px 30px;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 8px;
                    cursor: pointer;
                    box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
                ">
                    💾 اضغطي هنا لحفظ الشهادة كـ PDF أو طباعتها فوراً
                </button>
            </div>

            <style>
                @media print {
                    body * {
                        visibility: hidden;
                    }
                    #cert-print-area, #cert-print-area * {
                        visibility: visible;
                    }
                    #cert-print-area {
                        position: absolute;
                        left: 0;
                        top: 0;
                        width: 100%;
                        border: 8px double __BORDER__ !important;
                        box-shadow: none !important;
                        padding: 20px !important;
                    }
                }
            </style>
            """
            
            # دمج البيانات بأمان تام داخل التصميم
            certificate_html = html_template.replace("__BORDER__", border_color)\
                                            .replace("__BG__", bg_color)\
                                            .replace("__TCOLOR__", title_color)\
                                            .replace("__NAME__", student_to_certify)\
                                            .replace("__TITLE__", title)\
                                            .replace("__SCORE__", str(final_score))
                                            
            st.markdown(certificate_html, unsafe_allow_html=True)
