import pendulum
import re


def pick_date(begin: pendulum.DateTime, end: pendulum.DateTime, page, parent):
    """
    需要确保日期选择器在页面上显示
    微信后台日期选择器，选择特定的日期范围。
    跨度不能超过2个月
    """
    # 如果end - begin超过 2各月，throw exception
    if begin > end:
        raise ValueError("开始日期不能大于结束日期")
    if end >= pendulum.today():
        raise ValueError("结束日期必须早于今日")
    delta = pendulum.Interval(begin, end)
    if delta.in_months() >= 2:
        raise ValueError("日期选择器超出范围，开始结束时间相差不能超过2个月")

    def _abstract_year_month(date_str: str):
        match = re.search(r"(\d{4})年\s+(\d{1,2})月", date_str)
        if not match:
            raise ValueError("日历标题日期格式错误")
        return int(match.group(1)), int(match.group(2))

    # 打开日期选择器
    picker_icon = parent.query_selector(
        '//span[@class="weui-desktop-picker__icon-wrap"]'
    )
    picker_icon.click()
    page.wait_for_timeout(1000)

    pannels = parent.query_selector_all(
        '//dd[contains(@class, "weui-desktop-picker__dd")]/div[contains(@class, "weui-desktop-picker__panel_day")]'
    )
    if len(pannels) < 2:
        raise ValueError("日历面板数量错误")
    left_pannel, right_pannel, *_ = pannels

    left_head = left_pannel.query_selector(
        '//div[contains(@class, "weui-desktop-picker__panel__hd")]'
    )
    right_head = right_pannel.query_selector(
        '//div[contains(@class, "weui-desktop-picker__panel__hd")]'
    )

    # 选择begin
    # 判断是否进行日期翻页，计算点击 < or > 按钮的次数，并点击获取指定日期范围的日历
    # 如果begin小于left pannel head日期,需要向左翻页
    left_year, left_month = _abstract_year_month(left_head.inner_text())
    left_min_day = pendulum.date(left_year, left_month, 1)
    begin_delta = pendulum.Interval(left_min_day, pendulum.date(begin.year, begin.month, 1))
    left_delta_month = begin_delta.in_months()
    if left_delta_month < 0:
        for i in range(abs(left_delta_month)):
            left_pannel.query_selector("button").click()
            page.wait_for_timeout(500)
    # 如果begin大于righ pannel head日期，需要向右翻页
    if left_delta_month >= 2:
        for i in range(left_delta_month):
            right_pannel.query_selector("button").click()
            page.wait_for_timeout(500)

    # 定位begin对应的日期，点击
    _, left_month = _abstract_year_month(left_head.inner_text())
    (_, right_month,) = _abstract_year_month(right_head.inner_text())
    pannel = left_pannel if left_month == begin.month else right_pannel
    pannel.query_selector(
        f'//tbody//*//a[not(contains(@class, "weui-desktop-picker__faded")) and text()={begin.day}]'
    ).click()

    # 选择end
    right_year, right_month = _abstract_year_month(right_head.inner_text())
    right_min_day = pendulum.date(right_year, right_month, 1)
    end_delta = pendulum.Interval(right_min_day, pendulum.date(end.year, end.month, 1))
    right_delta_month = end_delta.in_months()
    if right_delta_month > 0:
        for i in range(right_delta_month):
            right_pannel.query_selector("button").click()
            page.wait_for_timeout(500)
    # 定位end对应的日期，点击
    _, left_month = _abstract_year_month(left_head.inner_text())
    (_, right_month,) = _abstract_year_month(right_head.inner_text())
    pannel = left_pannel if left_month == end.month else right_pannel
    pannel.query_selector(
        f'//tbody//*//a[not(contains(@class, "weui-desktop-picker__faded")) and text()={end.day}]'
    ).click()

    # 关闭picker
    picker_icon.click()