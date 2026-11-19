from flask import Blueprint, render_template
from database import Database
import pandas as pd

reports = Blueprint("reports", __name__)


@reports.route("/reports")
def reports_page():

    db = Database()

    # جلب البيانات من MySQL
    db.cursor.execute("""
        SELECT 
            payments.amount,
            payments.payment_status,
            payments.payment_date,
            subscriptions.price
        FROM payments
        INNER JOIN subscriptions
            ON payments.subscription_id = subscriptions.id
        WHERE payments.payment_status IN ('تم الدفع', 'paid')
    """)

    data = db.cursor.fetchall()

    # تحويل البيانات إلى DataFrame
    df = pd.DataFrame(
        data,
        columns=[
            "amount",
            "payment_status",
            "payment_date",
            "price"
        ]
    )

    # تحويل payment_date إلى تاريخ
    df["payment_date"] = pd.to_datetime(df["payment_date"])

    # إجمالي الإيرادات
    total_revenue = df["amount"].sum()

    # الإيرادات الشهرية
    monthly_revenue = (
        df.groupby(
            df["payment_date"].dt.to_period("M")
        )["amount"]
        .agg(["sum", "mean", "count", "max", "min"])
        .reset_index()
    )

    # تحويل الشهر إلى String حتى يستطيع Flask/Jinja التعامل معه بسهولة
    monthly_revenue["payment_date"] = (
        monthly_revenue["payment_date"].astype(str)
    )

    return render_template(
        "reports.html",
        total_revenue=total_revenue,
        monthly_revenue=monthly_revenue.to_dict("records")
    )