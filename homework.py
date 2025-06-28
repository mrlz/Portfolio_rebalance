import csv
from dateutil import parser
import copy

class Stock:
    price_per_date = {} # Faster to use a dictionary.
    name = "" # Allows us to identify the stock.

    def __init__(self, new_name):
        self.name = new_name
        self.price_per_date = {}

    def add_date_price(self, date, price): #Receives any arbitrary (date, price) tuple and stores it. Works according to Current Price function asked.
        self.price_per_date[date] = price
    
    def Price(self, date): #Returns price at given date.
        return self.price_per_date.get(date, fr"Unknown price of {self.name} for {date}.")


class Portfolio:
    stack_of_stocks = {}
    allocation = {}
    target_stock = {}

    def __init__(self):
        self.stack_of_stocks = {}
        self.allocation = {}
    
    def get_stack_of_stocks(self):
        return self.stack_of_stocks

    def add_new_stock(self, new_stock, units): #Adds a stock and its number of units to the portfolio.
        if units > 0:
            self.stack_of_stocks[new_stock.name] = [new_stock, units]
        else:
            print("Number of units must be positive.")

    def stock_allocation(self, new_allocation): #Overwrites the portfolio's stock allocation, when a new allocation is correctly provided.
        original_allocation = copy.deepcopy(self.allocation)
        self.allocation = {}
        total = 0
        for element in new_allocation:
            self.allocation[element] = new_allocation[element]
            total = total + new_allocation[element][1]
        if abs(total-1.0) < 0.00001: #Allocation must make sense. We will use an arbitrary tolerance value, noting that we could use more precise data types if needed.
            return True
        else:
            print("Allocation invalid. Values must add up to 1.0.")
            print("Please try again.")
            self.allocation = original_allocation
            return False
    
    def stock_distribution(self, query_date, target_stack=None): #Computes and returns stock distribution, with respect to current portfolio value.
        if target_stack is None: #We can also provide a stack of stocks to compute the distribution over that.
            target_stack = self.stack_of_stocks
        total_value = 0.0
        distribution = {}
        for stock_name in target_stack:
            stock, volume = target_stack[stock_name]
            current_value = stock.Price(query_date) * volume
            total_value = total_value + current_value
            distribution[stock_name] = current_value
        
        for stock_name in distribution:
            distribution[stock_name] = distribution[stock_name]/total_value
        
        return distribution, total_value

    def portfolio_rebalance(self, query_date, target_value=0, execute_trades=False):
        distribution, total_value = self.stock_distribution(query_date)
        print("")
        print(fr"Current portfolio, with value {total_value}, has distribution")
        print(distribution)
        print("\nWith current portfolio stock volumes")
        self.print_stack_of_stocks(self.stack_of_stocks)
        print("")

        #We separate in cases (just like mergesort)
        if self.allocation: #If there's an allocation.
            if distribution: #And we currently have stocks.
                self.target_stock = copy.deepcopy(self.stack_of_stocks)

                for stock_name in distribution: #We remove all stocks not present in allocation.
                    if not (stock_name in self.allocation):
                        print(fr"You must sell {self.target_stock[stock_name][1]} stocks of {stock_name}.")
                        del self.target_stock[stock_name]

                for stock_name in self.allocation: # And rebalance stocks in allocation -> Buy new types of stocks and modify existing ones accordingly.
                    stock, share = self.allocation[stock_name]
                    amount_to_move = ((share-distribution.get(stock_name, 0))*total_value)/stock.Price(query_date) #The stock object has the price for the given date.
                    if abs(amount_to_move) > 0.00001: #We define a tolerance, due to numerical precision. We can employ more precise data types, but this will suffice for the toy example.
                        if amount_to_move > 0:
                            print(fr"You must buy {abs(amount_to_move)} stocks of {stock_name}.")
                            self.target_stock[stock_name] = [stock, self.target_stock.get(stock_name, [stock, 0])[1] + amount_to_move]
                        elif amount_to_move < 0:
                            print(fr"You must sell {abs(amount_to_move)} stocks of {stock_name}.")
                            self.target_stock[stock_name] = [stock, self.target_stock.get(stock_name, [stock, 0])[1] + amount_to_move]
                    else:
                        print(fr"{stock_name} remains unchanged.")

            elif total_value == 0: #If we currently hold no stocks.
                if target_value > 0: #And a target value has been defined.
                    for stock_name in self.allocation:
                        stock, share = self.allocation[stock_name]
                        amount_to_move = (share*target_value)/stock.Price(query_date)
                        self.target_stock[stock_name] = [stock, amount_to_move]
                        print(fr"You must buy {amount_to_move} stocks of {stock_name}.")
                else: #If we currently hold no stocks, and no target value has been provided, it makes little sense to compute further.
                    print("Since portfolio is empty, you must provide a target value to balance.")
                    return

            print("\nTo reach portfolio stock volumes")
            self.print_stack_of_stocks(self.target_stock)
            target_distribution, target_total = self.stock_distribution(query_date, self.target_stock)
            print("\nWith stock distribution")
            print(target_distribution)
            print("")
            print(fr"Valued at {target_total}")

            if execute_trades:
                self.stack_of_stocks = self.target_stock
                
        else:
            print("Please define a portfolio allocation first.")
    
    #Quality of life function to print a stack of stocks.
    def print_stack_of_stocks(self, stack_of_stocks):
        printable = {}
        for stock_name in stack_of_stocks:
            printable[stock_name] = stack_of_stocks[stock_name][1]
        print(printable)

    #Legacy function from previous homework, left here for testing purposes.
    def Profit(self, start_date, end_date):
        total_profit = 0 # We'll collect the differences using this variable.
        clean_results = True # We want to sanity check the results. In case we're missing the value for any specified date, we want to alert the user.

        start_date_obj = parser.parse(start_date)
        end_date_obj = parser.parse(end_date)

        if start_date_obj < end_date_obj:
            for stock_name in self.stack_of_stocks: # Simple for loop over our stack of stocks.
                stock, amount = self.stack_of_stocks[stock_name]
                end_price = stock.Price(end_date) # Get the corresponding prices.
                start_price = stock.Price(start_date)
                end_price_problem = isinstance(end_price, str) # Check if we get the expected numerical price or the error message.
                start_price_problem = isinstance(start_price, str)
                if end_price_problem:
                    clean_results = False
                    print(end_price)
                if start_price_problem:
                    clean_results = False
                    print(start_price)
                if not (end_price_problem or start_price_problem):
                    total_profit = total_profit + amount*(end_price - start_price)
                    
            if clean_results:
                print(fr"All values correctly computed for current portfolio between {start_date} and {end_date}")
            else:
                print("Some values missing for current portfolio. Total profit calculation is not accurate.")
                
            return total_profit
        else:
            print("End date comes before start date.")
            return 0

#Simply load the stock data from the CSV file.
def load_stock_data(file_path = fr'./stock_details_5_years_csv.csv'):
    with open(file_path) as csvfile:
        reader = csv.reader(csvfile, delimiter = ",")
        header = next(reader)
        unique_stocks = {}
        for row in reader:
            company = row[8]
            stock = unique_stocks.get(company, Stock(company))
            stock.add_date_price(row[0], float(row[1]))
            unique_stocks[company] = stock
        
        print("########################################")
        print(fr"Total loaded stocks: {len(unique_stocks)}.")
        print("########################################")
        return unique_stocks

if __name__ == '__main__':
    
    ################################## Load stock data ###################################

    available_stocks = load_stock_data() # We'll load some sample data from https://www.kaggle.com/datasets/iveeaten3223times/massive-yahoo-finance-dataset

    ######################################################################################

    nvda_Portfolio = Portfolio() #The portfolio of an NVDA fanboy.

    #################### Define stocks and test portfolio ################################
    print("\n### Define stocks and test portfolio ###")


    NVDA = available_stocks['NVDA'] #This object contains the information of the Nvidia stock.

    print(fr"NVDA price at 2019-01-08 00:00:00-05:00 is {NVDA.Price("2019-01-08 00:00:00-05:00")}") #Should be 36.39084278.
    print(fr"NVDA price at 2022-05-23 00:00:00-04:00 is {NVDA.Price("2022-05-23 00:00:00-04:00")}") #Should be 162.5578276.

    nvda_Portfolio.add_new_stock(NVDA, 1)

    print("\n1 NVDA stock portfolio.")
    print(nvda_Portfolio.Profit('2019-01-08 00:00:00-05:00', '2022-05-23 00:00:00-04:00')) #Should be 126.16698482.
    print(nvda_Portfolio.Profit('2022-05-23 00:00:00-04:00', '2019-01-08 00:00:00-05:00')) #Should warn us of our folly.


    print("########################################")
    ######################################################################################

    ############################# Define a more diverse portfolio ########################
    print("\n### Define a more diverse portfolio ####")


    MSFT = available_stocks['MSFT'] #This object contains the information of the Microsoft stock.
    GOOGL = available_stocks['GOOGL'] #This object contains the information of the Google stock.
    AAPL = available_stocks['AAPL'] #This object contains the information of the AAPL stock.

    new_Portfolio = Portfolio()

    stocks_to_add = [[NVDA, 50], [MSFT, 70], [GOOGL, 30], [AAPL, 10]]

    for stock, quantity in stocks_to_add:
        new_Portfolio.add_new_stock(stock, quantity)

    current_date = '2023-11-29 00:00:00-05:00' #Last available date in toy dataset.

    print("")
    print(fr"Portfolio at {current_date} is comprised of")
    new_Portfolio.print_stack_of_stocks(new_Portfolio.get_stack_of_stocks())

    print("\nPortfolio distribution at 2023-11-29 00:00:00-05:00.")
    print(new_Portfolio.stock_distribution(current_date)[0]) #Our current distribution is ~ NVDA: 0.42, MSFT: 0.47, GOOGL: 0.07, AAPL: 0.03

    print("\nPortfolio distribution at 2019-01-08 00:00:00-05:00")
    print(new_Portfolio.stock_distribution('2019-01-08 00:00:00-05:00')[0]) #We can query other dates to see how the distribution shapes up.


    print("########################################")
    ######################################################################################

    ############################## Basic tests ###########################################

    empty_portfolio = Portfolio()

    print("Empty portfolio to empty allocation.")
    empty_allocation = {}
    empty_portfolio.stock_allocation(empty_allocation)
    empty_portfolio.portfolio_rebalance(current_date) #Does nothing.
    print("########################################")
    
    print("Empty portfolio to something in allocation.")
    simple_allocation = {'NVDA': [NVDA, 1]}
    empty_portfolio.stock_allocation(simple_allocation)
    empty_portfolio.portfolio_rebalance(current_date) #Will fail, since there are no stocks to rebalance.
    print("########################################")

    print("Empty portfolio to something in allocation, while providing target value.")
    simple_allocation = {'NVDA': [NVDA, 0.6], 'MSFT': [MSFT, 0.4]}
    empty_portfolio.stock_allocation(simple_allocation)
    empty_portfolio.portfolio_rebalance(current_date, 10000) #Note that, since the portfolio is empty, we must provide a target value for the rebalance to make sense.
    print("########################################")

    print("Rebalance portfolio with invalid allocation.")
    empty_portfolio = Portfolio()
    simple_allocation = {'NVDA': [NVDA, 0.59], 'MSFT': [MSFT, 0.39], 'AAPL': [AAPL, 0.01999]}
    empty_portfolio.stock_allocation(simple_allocation)
    empty_portfolio.portfolio_rebalance(current_date, 10000)
    print("########################################")

    print("Portfolio populated with stocks that differ from allocation.")
    populated_portfolio = Portfolio()
    stocks_to_add = [[GOOGL, 30], [AAPL, 10]]
    for stock, quantity in stocks_to_add:
        populated_portfolio.add_new_stock(stock, quantity)

    simple_allocation = {'NVDA': [NVDA, 0.6], 'MSFT': [MSFT, 0.4]}
    populated_portfolio.stock_allocation(simple_allocation)
    populated_portfolio.portfolio_rebalance(current_date) #Makes us sell all our currently held stocks, to purchase those in allocation.
    print("########################################")
    
    print("Allocation removes stock variety from portfolio.")
    populated_portfolio = Portfolio()
    stocks_to_add = [[GOOGL, 30], [AAPL, 10], [NVDA, 100], [MSFT, 50]]
    for stock, quantity in stocks_to_add:
        populated_portfolio.add_new_stock(stock, quantity)

    populated_portfolio.stock_allocation(simple_allocation)
    populated_portfolio.portfolio_rebalance(current_date, execute_trades=True) #We use the execute_trades parameter to actually modify the portfolio, according to the plan.
    print("########################################")

    print("Allocation matches current distribution of stocks.")
    populated_portfolio.portfolio_rebalance(current_date) #Since the portfolio was previously modified, no further changes should be necessary.
    print("########################################")
    ######################################################################################
    
    ############################# Test portfolio rebalance ###############################
    print("\n###### Test portfolio rebalance ########")
    stock_allocation = {'NVDA': [NVDA, 0.2], 'MSFT': [MSFT, 0.3], 'GOOGL': [GOOGL, 0.1], 'AAPL': [AAPL, 0.4]}

    new_Portfolio.stock_allocation(stock_allocation)

    print("\nTest a portfolio rebalance for (NVDA: 0.2, MSFT: 0.3, GOOGL: 0.1, AAPL: 0.4) allocation.")
    new_Portfolio.portfolio_rebalance(current_date)
    print("########################################")
    ######################################################################################

    
#We could further refine this to allow a portfolio composition per date, so that we can study a given portfolio's change through time.
#We could extend rebalance to take a target portfolio value at all times, and rebalance accordingly, while the default case is to just rebalance the current value.
