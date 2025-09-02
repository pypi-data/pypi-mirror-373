@given(u'<precondition>')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given <precondition>')


@when(u'<action>')
def step_impl(context):
    raise NotImplementedError(u'STEP: When <action>')


@then(u'<expected result>')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then <expected result>')


@given(u'<example precond. 1>')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given <example precond. 1>')


@when(u'<example action 1>')
def step_impl(context):
    raise NotImplementedError(u'STEP: When <example action 1>')


@then(u'<example result 1>')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then <example result 1>')


@given(u'<example precond. 2>')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given <example precond. 2>')


@when(u'<example action 2>')
def step_impl(context):
    raise NotImplementedError(u'STEP: When <example action 2>')


@then(u'<example result 2>')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then <example result 2>')