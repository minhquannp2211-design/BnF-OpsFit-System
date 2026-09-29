def raw_unit_cost(package_price, standard_package_quantity):
   raw_unit_cost = package_price / standard_package_quantity
   return raw_unit_cost

def usable_quantity(standard_package_quantity, waste_rate):
   usable_quantity = standard_package_quantity * (1 - waste_rate)
   return usable_quantity

def effective_unit_cost(usable_quantity, package_price ):
   effective_unit_cost = package_price / usable_quantity
   return effective_unit_cost

def ingredient_line_cost(standard_ingredient_quantity, effective_unit_cost ):
   ingredient_line_cost = standard_ingredient_quantity * effective_unit_cost
   return ingredient_line_cost

def unit_cogs(ingredient_line_cost):
   unit_cogs = 0
   n = len(ingredient_line_cost)
   for i in range(n):
      unit_cogs += ingredient_line_cost[i]
   return unit_cogs
def monthly_cost (amount, month_period):
   monthly_cost = amount / month_period
   return monthly_cost
def monthly_depreciation (amount, useful_life_months):
   monthly_depreciation = amount / useful_life_months
   return monthly_depreciation
def total_fixed_cost(monthly_cost, monthly_depreciation):
   total_monthly_cost = 0
   n = len(monthly_cost)
   for i in range(n):
      total_monthly_cost += monthly_cost[i]
   total_monthly_depreciation = 0
   n = len(monthly_depreciation)
   for i in range(n):
      total_monthly_depreciation += monthly_depreciation[i]
   total_fixed_cost = total_monthly_cost + total_monthly_depreciation
   return total_fixed_cost
def revenue(quantity_sold, food_price):
   revenue = quantity_sold * food_price
   return revenue
def total_revenue (revenue):
   total_revenue = 0
   n = len(revenue)
   for i in range(n):
      total_revenue += revenue[i]
   return total_revenue
def cogs(quantity_sold, unit_cogs):
   cogs = quantity_sold * unit_cogs
   return cogs
def total_cogs (cogs):
   total_cogs = 0
   n = len(cogs)
   for i in range(n):
      total_cogs += cogs[i]
   return total_cogs
def operating_cost(total_cogs, total_fixed_cost):
   operating_cost = total_fixed_cost + total_cogs
   return operating_cost
def operating_profit(operating_cost, total_revenue):
   operating_profit = total_revenue - operating_cost
   return operating_profit
def contribution_margin_unit(food_price, unit_cogs):
   contribution_margin_unit = food_price - unit_cogs
   return contribution_margin_unit
def contribution_margin_item(cogs, revenue):
   contribution_margin_item = revenue - cogs
   return contribution_margin_item
def total_contribution_margin(total_revenue, total_cogs):
   total_contribution_margin = total_revenue - total_cogs
   return total_contribution_margin
def contribution_margin_ratio(total_contribution_margin, total_revenue ):
   contribution_margin_ratio = total_contribution_margin / total_revenue
   return contribution_margin_ratio
def operating_profit_margin(operating_profit, total_revenue):
   operating_profit_margin = operating_profit / total_revenue
   return operating_profit_margin
def fixed_cost_ratio(total_fixed_cost, total_revenue):
   fixed_cost_ratio = total_fixed_cost / total_revenue
   return fixed_cost_ratio







