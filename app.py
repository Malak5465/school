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
# ⚙️ إعدادات الربط بـ Supabase (تم إدخال بياناتكِ الحقيقية)
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
# التبويب الأول: إدارة الطالبات (إضافة أسماء إلى السحاب)
# ----------------------------------------------------
with tab1:
    st.subheader("👧 إضافة طفلة جديدة للفصل")
    new_student = st.text_input("أدخلي اسم الطفلة كاملاً:")
    
    if st.button("إضافة الطفلة"):
        if new_student.strip() != "":
            student_name_clean = new_student.strip()
            try:
                # التحقق إذا كان الاسم مضافاً مسبقاً في جدول سوبابيس
                check_exist = supabase.table("students").select("*").eq("name", student_name_clean).execute()
                
                if check_exist.data:
                    st.warning("⚠️ هذه الطفلة مضافة بالفعل في الفصل.")
                else:
                    # إدخال الاسم يدوياً وبشكل دائم
                    supabase.table("students").insert({"name": student_name_clean}).execute()
                    st.success(f"✅ تم حفظ الطفلة ({student_name_clean}) في قاعدة البيانات بنجاح!")
            except Exception as e:
                st.error(f"حدث خطأ أثناء الحفظ السحابي: {e}")
        else:
            st.error("❌ الرجاء كتابة اسم الطفلة أولاً.")

# جلب قائمة أسماء الفصل من سوبابيس بشكل حي لتغذية باقي التبويبات
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
        
        # المعايير الأربعة المطلوبة
        behavior = st.slider("⭐ السلوك المتميز:", 1, 5, 5)
        hygiene = st.slider("⭐ النظافة والترتيب:", 1, 5, 5)
        participation = st.slider("⭐ المشاركة والتفاعل:", 1, 5, 5)
        activities = st.slider("⭐ حل الأنشطة والمهام:", 1, 5, 5)
        
        st.write("---")
        
        if st.button("حفظ التقييم السحابي"):
            day_total = behavior + hygiene + participation + activities
            try:
                # تجهيز البيانات للإرسال إلى جدول evaluations
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
        # عرض البيانات في جدول تفاعلي أنيق ومحدث
        df = pd.DataFrame(eval_records)
        st.dataframe(df[["student_name", "day_number", "total"]], use_container_width=True)
        
        st.write("---")
        st.markdown("#### 📜 إصدار الشهادات:")
        
        student_to_certify = st.selectbox("اختار الطالبة لإصدار الشهادة:", list(set(df["student_name"])))
        
        # حساب إجمالي درجات اليومين للطالبة المحددة من جدول سوبابيس
        student_rows = df[df["student_name"] == student_to_certify]
        final_score = int(student_rows["total"].sum())
        
        st.metric(label=f"المجموع الإجمالي لـ {student_to_certify} (من 40 درجة):", value=f"{final_score} / 40")
        
        # الفحص التلقائي وإطلاق اللقب
        if final_score == 40:
            st.balloons()
            st.success("🏆 اللقب المستحق تلقائياً: **نجم الأسبوع الخارق** 👑")
        elif final_score >= 32:
            st.info("🌟 اللقب المستحق تلقائياً: **البطل المتميز** ✨")
        else:
            st.warning("👍 اللقب المستحق تلقائياً: **البطل المجتهد** (بحاجة لبعض التحسين)")
            
        if st.button("🖨️ توليد وتحميل الشهادة"):
            st.info("⚙️ الخطوة القادمة والأخيرة هي ربط قالب الصورة الفعلي لطباعة هذه البيانات عليه!")
