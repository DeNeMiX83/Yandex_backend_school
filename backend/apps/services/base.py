def categories_recalculation(changed_categories):
    if not changed_categories:
        return
    new_changed_categories = set()
    for category in changed_categories:
        if category is None:
            continue
        category.recalculate_price()
        if category.parentId is not None:
            new_changed_categories.add(category.parentId)

    categories_recalculation(new_changed_categories)
