import streamlit as st
import pandas as pd

# إعدادات الصفحة الأساسية لتناسب الجوال والكمبيوتر
st.set_page_config(
    page_title="برنامج تقييم الأطفال",
    page_icon="👶",
    layout="centered"
)

# تصميم واجهة ترحيبية أنيقة باللغة العربية
st.markdown("<h1 style='text-align: center; color: #4A90E2;'>🌟 برنامج تقييم الأطفال اليومي 🌟</h1>", unsafe_style_allowed=True)
st.markdown("<p style='text-align: center; color: #777;'>أهلاً بكِ يا أستاذة ملاك. يمكنكِ رصد التقييمات وإصدار الشهادات بكل بساطة.</p>", unsafe_style_allowed=True)
st.write("---")

# تهيئة ذاكرة مؤقتة لتخزين الأسماء والتقييمات للتجربة
if "students_list" not in st.session_state:
    st.session_state.students_list = ["أحمد", "سارة", "مريم"] # أسماء تجريبية
if "evaluations_db" not in st.session_state:
    st.session_state.evaluations_db = []

# إنشاء التبويبات الثلاثة الرئيسية
tab1, tab2, tab3 = st.tabs(["➕ إدارة الطالبات", "📝 رصد التقييم اليومي", "🎓 الشهادات والنتائج"])

# ----------------------------------------------------
# التبويب الأول: إدارة الطالبات (إضافة أسماء)
# ----------------------------------------------------
with tab1:
    st.subheader("👧 إضافة طفلة جديدة للفصل")
    new_student = st.text_input("أدخلي اسم الطفلة كاملاً:")
    
    if st.button("إضافة الطفلة"):
        if new_student.strip() != "":
            if new_student not in st.session_state.students_list:
                st.session_state.students_list.append(new_student)
                st.success(f"✅ تم إضافة الطفلة ({new_student}) بنجاح!")
            else:
                st.warning("⚠️ هذا الاسم موجود بالفعل في القائمة.")
        else:
            st.error("❌ الرجاء كتابة اسم الطفلة أولاً.")

# ----------------------------------------------------
# التبويب الثاني: رصد التقييم اليومي
# ----------------------------------------------------
with tab2:
    st.subheader("✍️ رصد درجات اليوم")
    
    if not st.session_state.students_list:
        st.info("💡 الرجاء إضافة طالبات أولاً من تبويب إدارة الطالبات.")
    else:
        # اختيار اسم الطفلة واليوم
        selected_student = st.selectbox("اكتبي أو اختاري اسم الطفلة:", st.session_state.students_list)
        selected_day = st.radio("تحديد اليوم:", ["اليوم الأول", "اليوم الثاني"], horizontal=True)
        
        st.write("---")
        st.markdown("#### 🌟 معايير التقييم (من 1 إلى 5 نجوم):")
        
        # أشرطة التقييم للمعايير الأربعة
        behavior = st.slider("⭐ السلوك المتميز:", 1, 5, 5)
        hygiene = st.slider("⭐ النظافة والترتيب:", 1, 5, 5)
        participation = st.slider("⭐ المشاركة والتفاعل:", 1, 5, 5)
        activities = st.slider("⭐ حل الأنشطة والمهام:", 1, 5, 5)
        
        st.write("---")
        
        if st.button("حفظ التقييم"):
            # حساب المجموع لليوم الحالي
            day_total = behavior + hygiene + participation + activities
            
            # حفظ التقييم في الذاكرة المؤقتة
            evaluation_record = {
                "student": selected_student,
                "day": selected_day,
                "behavior": behavior,
                "hygiene": hygiene,
                "participation": participation,
                "activities": activities,
                "total": day_total
            }
            st.session_state.evaluations_db.append(evaluation_record)
            st.success(f"🎉 تم حفظ تقييم {selected_student} لـ ({selected_day}) بمجموع {day_total} من 20!")

# ----------------------------------------------------
# التبويب الثالث: الشهادات والنتائج
# ----------------------------------------------------
with tab3:
    st.subheader("🏆 لوحة التحكم والشهادات التلقائية")
    
    if not st.session_state.evaluations_db:
        st.info("💡 لم يتم رصد أي تقييمات بعد. قومي برصد الدرجات لتظهر هنا.")
    else:
        # تحويل البيانات المؤقتة إلى جدول لعرضها
        df = pd.DataFrame(st.session_state.evaluations_db)
        st.dataframe(df[["student", "day", "total"]], use_container_width=True)
        
        st.write("---")
        st.markdown("#### 📜 إصدار الشهادات:")
        
        # اختيار اسم الطالبة لإصدار شهادتها
        student_to_certify = st.selectbox("اختار الطالبة لإصدار الشهادة:", list(set(df["student"])))
        
        # حساب مجموع اليومين للطالبة المختارة
        student_rows = df[df["student"] == student_to_certify]
        final_score = student_rows["total"].sum()
        
        st.metric(label=f"المجموع الإجمالي لـ {student_to_certify} (من 40 درجة):", value=f"{final_score} / 40")
        
        # ذكاء النظام في تحديد اللقب المستحق
        if final_score == 40:
            st.balloons()
            st.success("🏆 اللقب المستحق تلقائياً: **نجم الأسبوع الخارق** 👑")
        elif final_score >= 32:
            st.info("🌟 اللقب المستحق تلقائياً: **البطل المتميز** ✨")
        else:
            st.warning("👍 اللقب المستحق تلقائياً: **البطل المجتهد** (بحاجة لبعض التحسين)")
            
        if st.button("🖨️ توليد وتحميل الشهادة"):
            st.info("⚙️ في الخطوة القادمة، سنربط هذا الزر ليقوم بطباعة الاسم على الشهادة فوراً!")
