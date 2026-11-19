from database import Database
from user_form import Users
from flask import Flask, render_template, redirect,url_for, session,request
from subscripe_form import Subscripe
from category import Cat
from datetime import date,timedelta
from form_payment import Payment
from form_coach import coash
from reports import reports
from lgon    import loginFom
from ai import analyze
web = Flask(__name__)

web.config["SECRET_KEY"] = "hhfhfdhkdwkowdkjjkgfkljgfklglfglk"


@web.route("/insert_user", methods=["POST", "GET"])
def insert():

    db = Database()

    form = Users()


    if form.validate_on_submit():
      name  =   form.name.data
      phone =  form.phone.data
      age   =   form.age.data
      role = 'user'

      if age < 18:
         category_id= 1
      elif age < 40:
         category_id=2
      else:
         category_id=3
      db.cursor.execute("INSERT INTO users(name,phone,age,category_id,role) VALUES(%s,%s,%s,%s,%s)",(name,phone,age,category_id,role))
   
      db.conn.commit()

      user_id = db.cursor.lastrowid

      session["user_id"] = user_id
      
      return redirect(url_for("insert_subscripe"))
   
    return render_template("insert_user.html", form=form)





@web.route("/insert_subscriptions", methods=["GET", "POST"])
def insert_subscripe():

    db = Database()

    form = Subscripe()

    user_id = session.get("user_id")

    status = "active"

    start_date = date.today()

    if form.validate_on_submit():

        print("FORM OK")

        # السعر الذي أدخله الموظف في النموذج
        price = form.price.data

        # الخطة المختارة
        plan_id = int(form.plan_id.data)

        # تحديد مدة الاشتراك
        if plan_id == 1:

            duration = 30

        elif plan_id == 2:

            duration = 90

        elif plan_id == 3:

            duration = 365

        else:

            return "Invalid Plan"

        # حساب تاريخ النهاية
        end_date = start_date + timedelta(days=duration)

        print("PRICE =", price)
        print("PLAN ID =", plan_id)
        print("START DATE =", start_date)
        print("END DATE =", end_date)

        # إدخال الاشتراك
        db.cursor.execute(
            """
            INSERT INTO subscriptions
            (
                user_id,
                start_date,
                end_date,
                price,
                status,
                plan_id
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                start_date,
                end_date,
                price,
                status,
                plan_id
            )
        )

        db.conn.commit()

        return redirect(url_for("select_user_subscripe"))

    else:

        print(form.errors)

    return render_template(
        "insert_subscriptions.html",form=form)


@web.route("/select_users_subscripe", methods=['GET','POST'])
def select_user_subscripe():

    db = Database()

    db.cursor.execute("""
    SELECT 
        users.id,
        users.name,
        subscriptions.end_date,
        subscriptions.status,
        plan_subscriptions.plan,
        category.name,
        attendace.status,
        subscriptions.id,
        payments.payment_status,
        attendace.id
        


    FROM subscriptions

    INNER JOIN users 
    ON subscriptions.user_id = users.id

    INNER JOIN category 
    ON users.category_id = category.id

    INNER JOIN plan_subscriptions 
    ON subscriptions.plan_id = plan_subscriptions.id
   LEFT JOIN attendace 
   ON attendace.user_id = users.id
   AND attendace.attendance_date = CURDATE() 
      LEFT JOIN payments
      ON payments.subscription_id = subscriptions.id   """)


    users_plan_sub = db.cursor.fetchall()

    return render_template(
        "select_users_subscripe.html",
        users_plan_sub=users_plan_sub
    )









@web.route("/attendance/<int:user_id>", methods=["GET","POST"])
def insert_attendance(user_id):

    db = Database()


    # هل سجل حضور اليوم موجود؟
    db.cursor.execute("""
        SELECT *
        FROM attendace
        WHERE user_id=%s
        AND attendance_date = CURDATE()

    """,(user_id,))


    attendance = db.cursor.fetchone()



    # إذا موجود لا يكرر
    if attendance:

        return "تم تسجيل الحضور مسبقا"



    # إنشاء سجل جديد
    db.cursor.execute("""
        INSERT INTO attendace
        (
            user_id,
            attendance_date,
            status
        )

        VALUES
        (
            %s,
            CURDATE(),
            'present'
        )

    """,(user_id,))



    db.conn.commit()


    return redirect(url_for("select_user_subscripe"))






@web.route("/insert_payment/<int:user_id>",methods=["GET","POST"])

def insert_payment(user_id):
    db = Database()
   



    db.cursor.execute("""
SELECT id, price
FROM subscriptions
WHERE user_id=%s
AND status='active'
ORDER BY id DESC
LIMIT 1
""",(user_id,))


    subscription = db.cursor.fetchone()


    subscription_id = subscription[0]
    amount = subscription[1]
    form  = Payment()
    payment_date = date.today()
    if form.validate_on_submit():
     
      payment_method = form.payment_method.data
      if payment_method=="cash":
           payment_status = 'تم الدفع'
     
           db.cursor.execute("SELECT id FROM payments WHERE subscription_id=%s",(subscription_id,))
           sub = db.cursor.fetchone()

           if sub:
               return "تم الدفع مسبقا"

           
           db.cursor.execute("INSERT INTO payments(user_id,subscription_id,amount,payment_method,payment_status,payment_date) VALUES(%s,%s,%s,%s,%s,%s)",(user_id,subscription_id,amount,payment_method,payment_status,payment_date))  
           db.conn.commit()
           return "تم التسجيل بنجاح" 
          
      elif payment_method=="visa":
       return  redirect(url_for("visa_payment",user_id=user_id))
    

    return render_template("insert_paid.html",form=form)         


@web.route("/visa_payment/<int:user_id>", methods=["GET","POST"])
def visa_payment(user_id):

    return render_template("visa_payment.html",user_id=user_id)
       







# squire search  

@web.route("/search_user_sub",methods=["POST"])
def search_user_sub():
    db = Database()
    search = request.form["search"]

    db.cursor.execute(""" SELECT
    
    
    
    
    users.id,
    users.name,
    users.phone,
    users.age,

    category.name AS category_name,

    plan_subscriptions.plan,

    subscriptions.start_date,
    subscriptions.end_date,
    subscriptions.status,
    subscriptions.price,

    payments.payment_status


FROM users


INNER JOIN category
ON users.category_id = category.id


INNER JOIN subscriptions
ON subscriptions.user_id = users.id


INNER JOIN plan_subscriptions
ON subscriptions.plan_id = plan_subscriptions.id


LEFT JOIN payments
ON payments.subscription_id = subscriptions.id
    
  
WHERE users.name LIKE %s OR  users.phone LIKE %s  




     """,(

         "%"+search+"%",
         "%"+search+"%"
     ))



    one_sub = db.cursor.fetchall()
    return render_template("search_user_sub.html",one_sub=one_sub)




@web.route("/update_attendace/<int:id>",methods=["GET","POST"])
def update_attendace(id):
    db = Database()

    db.cursor.execute("SELECT status FROM attendace  WHERE id=%s",(id,))
    status_user = db.cursor.fetchone()[0]
    if status_user=='present':
        status_user='absent'
    else:
        status_user='present'   

    db.cursor.execute("UPDATE attendace SET status=%s WHERE id = %s",(status_user,id))
    db.conn.commit()
    return redirect(url_for("select_user_subscripe"))




@web.route("/insert_coash",methods=["GET","POST"])
def insert_coach():
    db = Database()
    form = coash()
    db.cursor.execute("SELECT id,name FROM category ")
             
    cat_id = db.cursor.fetchall()
    if form.validate_on_submit():
       name   = form.name.data

       phone  = form.phone.data

       age    = form.age.data

       category_id = request.form["select"]
       specialty = form.specialty.data
       


       db.cursor.execute("INSERT INTO coaches(name,phone,age,category_id,specialty) VALUES (%s,%s,%s,%s,%s)",(name,phone,age,category_id,specialty))
       db.conn.commit()
       coash_id = db.cursor.lastrowid
       session['coash_id'] = coash_id 

       return redirect(url_for('insert_coach'))
    return render_template("insert_coah.html",form=form,cat_id=cat_id)






@web.route("/select_coash_user", methods=["GET", "POST"])
def select_coash_user():

    db = Database()

    if request.method == "POST":

        search = request.form.get("search")

        db.cursor.execute("""
            SELECT *
            FROM users
            WHERE name LIKE %s
               OR phone LIKE %s
        """,
        (
            "%" + search + "%",
            "%" + search + "%"
        ))

    else:

        db.cursor.execute("""
            SELECT *
            FROM users
        """)

    users = db.cursor.fetchall()

    return render_template(
        "search_user.html",
        users=users
    )
# ==========================================
# حفظ المدرب
# ==========================================
@web.route("/assign_coash_user/<int:user_id>")
def assign_coash_user(user_id):

    db = Database()

    db.cursor.execute("""
        SELECT *
        FROM users
        WHERE id=%s
    """, (user_id,))

    user = db.cursor.fetchone()

    db.cursor.execute("""
        SELECT *
        FROM coaches
    """)

    coaches = db.cursor.fetchall()

    return render_template(
        "assign_coach.html",
        user=user,
        coaches=coaches
    )





@web.route("/assign_coach", methods=["POST"])
def assign_coach():

    db = Database()

    user_id = request.form.get("user_id")
    coach_id = request.form.get("coach_id")

    db.cursor.execute("""
        INSERT INTO user_coash
        (
            user_id,
            coash_id,
            date_at
        )
        VALUES
        (
            %s,
            %s,
            CURDATE()
        )
    """,
    (
        user_id,
        coach_id
    ))

    db.conn.commit()

    return redirect(url_for("select_coash_user"))

@web.route("/dashpord", methods=["GET"])
def dashpord():


    if 'user_id' not in session:
        return redirect(url_for('login'))


    if session.get('role') !='admin':
         return "ليس لديك صلاحية للوصول إلى لوحة التحكم", 403


    db = Database()


    

    # ==============================
    # عدد المدربين
    # ==============================

    db.cursor.execute("""
        SELECT COUNT(*) 
        FROM coaches
    """)

    coashes_count = db.cursor.fetchone()[0]



    # ==============================
    # عدد الاشتراكات
    # ==============================

    db.cursor.execute("""
        SELECT COUNT(*) 
        FROM subscriptions
    """)

    subscriptions_count = db.cursor.fetchone()[0]



    # ==============================
    # جلب بيانات المشتركين
    # ==============================

    db.cursor.execute(""" 
        SELECT 
            users.id,
            users.name,
            users.phone,
            users.age,
            category.name AS category_name

        FROM users

        INNER JOIN category

        ON users.category_id = category.id

    """)


    members = db.cursor.fetchall()
    db.cursor.execute("""
                SELECT 
                users.name,
                users.phone,
                attendace.status,
                attendace.attendance_date
                 
    
                FROM attendace
    
                INNER JOIN users ON attendace.user_id = users.id
                WHERE attendance_date = CURDATE()
        
            """)
        
        
    attendance = db.cursor.fetchall()



    db.cursor.execute("SELECT COUNT(*) FROM user_coash") 
    user_with_coash = db.cursor.fetchone()[0]


        
    
    db.cursor.execute("SELECT COUNT(*)  FROM subscriptions WHERE status='active'")
    all_activity = db.cursor.fetchone()[0]
    


    db.cursor.execute("""
    SELECT SUM(amount)
    FROM payments
    WHERE MONTH(payment_date) = MONTH(CURDATE())
    AND YEAR(payment_date) = YEAR(CURDATE())
""")

    to_month = db.cursor.fetchone()[0] or 0



    return render_template(
        "dashpord.html",
        coashes=coashes_count,
        sub=subscriptions_count,
        members=members,attendance=attendance,
        all_activity=all_activity,
        to_month=to_month,
        user_with_coash=user_with_coash
    )




@web.route("/select_coash",methods=["GET","POST"])
def select_coash():
    db = Database()
    db.cursor.execute(""" SELECT 
    coaches.id, 
    coaches.name,
    coaches.phone,
    coaches.age,
    category.name,
    coaches.specialty
    
    FROM coaches
    INNER JOIN category ON coaches.category_id =  category.id




""")


    coashes = db.cursor.fetchall()



    





   



    

   

    return render_template("select_coash.html",coashes=coashes)



@web.route("/remove_coash/<int:id>",methods=['GET'])
def remove_coash(id):
    db = Database()
    db.cursor.execute("DELETE FROM coaches WHERE id=%s" ,(id,))
    db.conn.commit()
    return redirect(url_for('select_coash'))



@web.route("/user_sub",methods=["GET","POST"])

def select_user_sub():
   db = Database()
   # تحديث الاشتراكات المنتهية تلقائياً
   db.cursor.execute("""
    UPDATE subscriptions
    SET status = 'expired'
    WHERE end_date < CURDATE()
      AND status = 'active'
""")

   db.conn.commit()
   db.cursor.execute(""" SELECT 

   users.id,
   users.name,
   users.phone,
   users.age,
   category.name,
   subscriptions.start_date,
   subscriptions.end_date,
   subscriptions.price,
   subscriptions.status,
   plan_subscriptions.plan
   FROM  subscriptions

   INNER JOIN users ON subscriptions.user_id = users.id
   INNER JOIN category ON  users.category_id = category.id
   INNER JOIN plan_subscriptions ON subscriptions.plan_id = plan_subscriptions.id


 






""")


   user_Sub  = db.cursor.fetchall()

   db.cursor.execute("""
    SELECT COUNT(*)
    FROM subscriptions
    WHERE status = 'active'
""")

   all_activity = db.cursor.fetchone()[0]

   

   db.cursor.execute("""
    SELECT COALESCE(SUM(amount), 0)
    FROM payments
    WHERE payment_status = 'تم الدفع'
""")

   sum_sub = db.cursor.fetchone()[0]  



   db.cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE end_date < CURDATE()")
   sum_expired = db.cursor.fetchone()[0]
   return render_template("/select_user_sub.html",user_sub=user_Sub,all_activity=all_activity,sum_sub=sum_sub,sum_expired=sum_expired)





@web.route("/ai_assistant", methods=["GET","POST"])
def ai_assistant():

    answer = ""

    if request.method == "POST":

        question = request.form["question"]


        db = Database()


        db.cursor.execute("""
        SELECT 
        users.name,
        users.age,
        subscriptions.status,
        subscriptions.price

        FROM users

        LEFT JOIN subscriptions
        ON users.id = subscriptions.user_id

        """)


        data = db.cursor.fetchall()

        db.cursor.execute(""" SELECT 

        coaches.id,
        coaches.name,
        coaches.phone,
        coaches.age,
        coaches.specialty,
        category.name

        FROM coaches

        INNER JOIN category ON coaches.category_id =  category.id





""")
        coashes = db.cursor.fetchall()

        prompt = f"""

أنت مساعد ذكي لإدارة نادي رياضي.

بيانات النادي:

{data}




بيانات المدربين : 

{coashes}

سؤال المدير:

{question}

قواعد الإجابة:
- لا تخترع معلومات غير موجودة.
- اعتمد فقط على البيانات المرسلة.
- إذا لم توجد معلومة قل لا توجد بيانات كافية.

"""

        answer = analyze(prompt)



    return render_template(
        "ai_assistant.html",
        answer=answer
    )


    




@web.route("/select_sub_acticity", methods=["GET", "POST"])
def select_sub_activity():

    db = Database()

    db.cursor.execute("""
        SELECT 
            users.id,
            users.name,
            users.age,
            category.name,
            subscriptions.start_date,
            subscriptions.end_date,
            subscriptions.price,
            plan_subscriptions.plan
        FROM subscriptions
        INNER JOIN users
            ON subscriptions.user_id = users.id
        INNER JOIN plan_subscriptions
            ON subscriptions.plan_id = plan_subscriptions.id
        INNER JOIN category
            ON users.category_id = category.id
        WHERE subscriptions.status = 'active'
    """)

    user_activity = db.cursor.fetchall()

    return render_template(
        "select_sub_acticity.html",
        user_activity=user_activity
    )


@web.route("/page_revenue",methods=["GET"])
def select_revenue():
   db = Database()
   db.cursor.execute("""  SELECT 
    
users.id,
users.name,
users.phone,
payments.amount,
payments.payment_date,
payments.payment_status,
plan_subscriptions.plan,
payments.id
FROM subscriptions
INNER JOIN users ON subscriptions.user_id = users.id
INNER JOIN plan_subscriptions ON subscriptions.plan_id = plan_subscriptions.id
INNER JOIN payments  ON    payments.subscription_id = subscriptions.id 





    """)

   all_rev = db.cursor.fetchall()

   return  render_template("page_revenue.html",all_rev=all_rev)  


@web.route("/select_user_expired", methods=["GET"])
def select_user_expired():

    db = Database()

    # تحديث الاشتراكات التي انتهت
    db.cursor.execute("""
        UPDATE subscriptions
        SET status = 'expired'
        WHERE end_date < CURDATE()
    """)

    db.conn.commit()

    # جلب الاشتراكات المنتهية فقط
    db.cursor.execute("""
        SELECT 
            users.id,
            users.name,
            users.phone,
            users.age,
            category.name,
            subscriptions.start_date,
            subscriptions.end_date,
            subscriptions.price,
            subscriptions.status,
            plan_subscriptions.plan,
            subscriptions.id,
            subscriptions.plan_id

        FROM subscriptions

        INNER JOIN users
            ON subscriptions.user_id = users.id

        INNER JOIN category
            ON users.category_id = category.id

        INNER JOIN plan_subscriptions
            ON subscriptions.plan_id = plan_subscriptions.id

        WHERE subscriptions.end_date < CURDATE()
    """)

    all_expired = db.cursor.fetchall()

    return render_template(
        "select_user_expired.html",
        all_expired=all_expired
    )





@web.route("/select_payment_to_month",methods=["GET"])
def select_payment_to_month():
   db = Database()
   db.cursor.execute("""  SELECT 
    
users.id,
users.name,
users.phone,
payments.amount,
payments.payment_date,
payments.payment_status,
plan_subscriptions.plan

FROM subscriptions
INNER JOIN users ON subscriptions.user_id = users.id
INNER JOIN plan_subscriptions ON subscriptions.plan_id = plan_subscriptions.id
INNER JOIN payments  ON    payments.subscription_id = subscriptions.id 

WHERE MONTH(payments.payment_date) = MONTH(payments.payment_date)

AND  YEAR(payments.payment_date)   = YEAR(payments.payment_date)



    """)

   to_month_select= db.cursor.fetchall()

   return  render_template("select_payment_to_month.html",to_month_select=to_month_select)  
@web.route("/update_subscription", methods=["POST"])
def update_subscription():

    db = Database()

    id          = request.form["id"]
    start_date  = request.form["start_date"]
    end_date    = request.form["end_date"]
    price       = request.form["price"]
    plan_id     = request.form["plan_id"]

    # 1️⃣ تحديث الاشتراك الحالي
    db.cursor.execute("""
        UPDATE subscriptions
        SET
            start_date = %s,
            end_date = %s,
            price = %s,
            plan_id = %s,
            status = CASE
                WHEN %s >= CURDATE()
                THEN 'active'
                ELSE 'expired'
            END
        WHERE id = %s
    """, (
        start_date,
        end_date,
        price,
        plan_id,
        end_date,
        id
    ))

    # 2️⃣ تسجيل الدفعة الجديدة
    db.cursor.execute("""
        INSERT INTO payments
        (
            subscription_id,
            amount,
            payment_date,
            payment_status
        )
        VALUES
        (
            %s,
            %s,
            CURDATE(),
            'paid'
        )
    """, (
        id,
        price
    ))

    db.conn.commit()

    return "Subscription renewed successfully"

@web.route("/update_coash",methods=["GET","POST"])
def update_coash():
    db = Database()

    id        = request.form['id']
    name      = request.form['name']
    phone     = request.form['phone']
    age       = request.form['age']
    specialty = request.form['specialty']
    
    db.cursor.execute("""
        UPDATE coaches
        SET
            name = %s,
            phone = %s,
            age = %s,
            specialty = %s
        WHERE id = %s
    """, (
        name,
        phone,
        age,
        specialty,
        id
    ))

    db.conn.commit()

    return "Coach updated successfully"






@web.route("/remove_one_player/<int:id>",methods=['GET','POST'])

def remove_one_user(id):
   db = Database()
   db.cursor.execute(
        "DELETE FROM subscriptions WHERE user_id = %s",
        (id,)
    )

    # حذف المشترك
   db.cursor.execute(
        "DELETE FROM users WHERE id = %s",
        (id,)
    )
   db.conn.commit()

   return redirect(url_for("select_user_sub"))



@web.route("/update_user", methods=["POST"])
def update_user():
    db = Database()

    id = request.form["id"]
    name = request.form["name"]
    phone = request.form["phone"]
    age = request.form["age"]

    db.cursor.execute("""
        UPDATE users
        SET name=%s, phone=%s, age=%s
        WHERE id=%s
    """, (name, phone, age, id))

    db.conn.commit()

    


@web.route("/delete_paymants/<int:id>", methods=["GET"])
def del_one_payment(id):

    db = Database()

    # أولاً: معرفة الاشتراك المرتبط بالدفع
    db.cursor.execute(
        "SELECT subscription_id FROM payments WHERE id = %s",
        (id,)
    )

    payment = db.cursor.fetchone()

    if not payment:
        return "Payment not found"

    subscription_id = payment[0]

    # ثانياً: جعل الاشتراك منتهي
    db.cursor.execute(
        "UPDATE subscriptions SET status = 'expired' WHERE id = %s",
        (subscription_id,)
    )

    # ثالثاً: حذف سجل الدفع
    db.cursor.execute(
        "DELETE FROM payments WHERE id = %s",
        (id,)
    )

    # رابعاً: تثبيت التغييرات
    db.conn.commit()

    return "Subscription cancelled successfully"









@web.route('/select_user_coash_for_sub',methods=['GET'])

def user_coash_for_sub():
    db = Database()
    db.cursor.execute(""" SELECT
    users.name,
    users.phone,
    category.name,
    coaches.name,
    coaches.phone,
    coaches.age,
    coaches.specialty
FROM category
INNER JOIN users
    ON users.category_id = category.id
INNER JOIN coaches
    ON coaches.category_id = category.id
    
    """)


    all = db.cursor.fetchall()
    return render_template("select_user_for_customer.html",all=all)




@web.route('/insert_admin', methods=['GET', 'POST'])
def insert_admin():
    form = Users()
    db = Database()

   
    if form.validate_on_submit():

        name = form.name.data
        phone = form.phone.data
        age = form.age.data

        db.cursor.execute(
            """
            INSERT INTO users
            (name, phone, age, category_id)
            VALUES (%s, %s, %s, %s)
            """,
            (name, phone, age, None)
        )

        db.conn.commit()

        admin_id = db.cursor.lastrowid

        session['user_id'] = admin_id
        session['role'] = 'admin'

        return redirect(url_for("dashpord"))

    return render_template("insert_admin.html", form=form)
@web.route('/login', methods=['GET', 'POST'])
def login():

    form = loginFom()
    db = Database()

    if form.validate_on_submit():

        # ==================================
        # البيانات القادمة من الفورم
        # ==================================

        name = form.name.data
        phone = form.phone.data

        # ==================================
        # البحث عن المستخدم بالاسم والهاتف
        # (بدون عمود role لأن غير موجود)
        # ==================================

        db.cursor.execute("""
            SELECT id
            FROM users
            WHERE name = %s
            AND phone = %s
        """, (name, phone))

        user = db.cursor.fetchone()

        # ==================================
        # إذا لم نجد المستخدم
        # ==================================

        if not user:
            return "الاسم أو رقم الهاتف غير صحيح", 401

        # ==================================
        # أخذ بيانات المستخدم
        # ==================================

        user_id = user[0]
        role = 'admin'          # ← نعينه يدوياً مؤقتاً

        # ==================================
        # حفظ المستخدم في Session
        # ==================================

        session['user_id'] = user_id
        session['role'] = role

        # ==================================
        # تحديد الصفحة حسب Role
        # ==================================

        if role == 'admin':
            return redirect(url_for('dashpord'))

        elif role == 'employee':
            return redirect(url_for('employee_dashboard'))

        elif role == 'user':
            return redirect(url_for('select_user_expired'))

        else:
            return "الدور غير معروف", 403

    return render_template(
        "login.html",
        form=form
    )


@web.route("/logout_admin",methods=["GET"])


def logout_foradmin():

  session.clear()
  return redirect(url_for("login"))







@web.route("/insert_category", methods=["GET", "POST"])
def insert_category():

    db = Database()
    form = Cat()

    # =========================
    # إضافة فئة جديدة
    # =========================
    if form.validate_on_submit():

        name = form.name.data.strip()

        if name:

            db.cursor.execute(
                """
                INSERT INTO category (name)
                VALUES (%s)
                """,
                (name,)
            )

            db.conn.commit()

        return redirect(url_for("insert_category"))

    # =========================
    # جلب الفئات من قاعدة البيانات
    # =========================
    db.cursor.execute(
        """
        SELECT id, name
        FROM category
        ORDER BY id DESC
        """
    )

    rows = db.cursor.fetchall()

    # تحويل البيانات إلى dictionaries
    categories = []

    for row in rows:
        categories.append({
            "id": row[0],
            "name": row[1]
        })

    # =========================
    # عرض الصفحة
    # =========================
    return render_template(
        "insert_category.html",
        form=form,
        categories=categories
    )


@web.route("/delete_category/<int:id>", methods=["GET"])
def remove_cat(id):
    db = Database()

    db.cursor.execute(
        "DELETE FROM category WHERE id = %s",
        (id,)
    )

    db.conn.commit()

    return redirect(url_for("insert_category"))


web.register_blueprint(reports)




if __name__ == "__main__":
    web.run(debug=True)
