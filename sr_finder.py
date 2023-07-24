import os
import time
from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import historical_data
import indicators_sma_rsi
import support_resistance


@dataclass
class Values:
    ticker_csv: str
    selected_timeframe: str

    def __post_init__(self):
        self.ticker_csv = self.ticker_csv.upper()
        self.selected_timeframe = self.selected_timeframe.lower()


class Supres:
    support_list = []
    resistance_list = []
    fibonacci_uptrend  = []
    fibonacci_downtrend = []
    pattern_list = []
    support_above = []
    support_below = []
    resistance_below = []
    resistance_above = []
    x_dat = []
    df = []
    x_date = ""
    fig = None
    selected_timeframe = ""
    ticker_csv = ""

    fibonacci_multipliers = 0.236, 0.382, 0.500, 0.618, 0.705, 0.786, 0.886
    # Chart settings
    (
        legend_color,
        chart_color,
        background_color,
        support_line_color,
        resistance_line_color,
    ) = ("#D8D8D8", "#E7E7E7", "#E7E7E7", "LightSeaGreen", "MediumPurple")
    historical_hightimeframe = (
        historical_data.Client.KLINE_INTERVAL_1DAY,
        historical_data.Client.KLINE_INTERVAL_3DAY,
        historical_data.Client.KLINE_INTERVAL_1WEEK,
    )
    historical_lowtimeframe = (
        historical_data.Client.KLINE_INTERVAL_1MINUTE,
        historical_data.Client.KLINE_INTERVAL_3MINUTE,
        historical_data.Client.KLINE_INTERVAL_5MINUTE,
        historical_data.Client.KLINE_INTERVAL_15MINUTE,
        historical_data.Client.KLINE_INTERVAL_30MINUTE,
        historical_data.Client.KLINE_INTERVAL_1HOUR,
        historical_data.Client.KLINE_INTERVAL_2HOUR,
        historical_data.Client.KLINE_INTERVAL_4HOUR,
        historical_data.Client.KLINE_INTERVAL_6HOUR,
        historical_data.Client.KLINE_INTERVAL_8HOUR,
        historical_data.Client.KLINE_INTERVAL_12HOUR,
    )
    sma_values = 20, 50, 100

    def main(self, ticker_csv, selected_timeframe, candle_count=254):
        print(
            f"Start main function in {time.perf_counter() - perf} seconds\n"
            f"{ticker_csv} data analysis in progress."
        )
        now_supres = time.perf_counter()
        self.df = pd.read_csv(
            ticker_csv,
            delimiter=",",
            encoding="utf-8-sig",
            index_col=False,
            nrows=candle_count,
            keep_default_na=False,
        )
        self.df = self.df.iloc[::-1]
        self.df["date"] = pd.to_datetime(self.df["date"], format="%Y-%m-%d")
        self.df = pd.concat([self.df, self.df.tail(1)], axis=0, ignore_index=True)
        self.df.dropna(inplace=True)
        self.selected_timeframe = selected_timeframe
        self.ticker_csv = ticker_csv
        sma1, sma2, sma3, rsi = indicators_sma_rsi.indicators(self.df[:-1], *self.sma_values)

        fibonacci_multipliers = 0.236, 0.382, 0.500, 0.618, 0.705, 0.786, 0.886
        # Chart settings
        (
            legend_color,
            chart_color,
            background_color,
            support_line_color,
            resistance_line_color,
        ) = ("#D8D8D8", "#E7E7E7", "#E7E7E7", "LightSeaGreen", "MediumPurple")
        self.fig = make_subplots(
            rows=3,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0,
            row_width=[0.1, 0.1, 0.8],
        )
        
        self.sensitivity()
        self.chart_lines()
        # # Checking if the selected timeframe is in the historical_hightimeframe list.
        if selected_timeframe in self.historical_hightimeframe:
            self.candlestick_patterns()
            self.x_date = "%b-%d-%y"
        elif selected_timeframe in self.historical_lowtimeframe:
            self.x_date = "%H:%M %d-%b"
        self.create_candlestick_plot()
        self.chart_updates()
        self.save(candle_count)
        # pinescript_code(historical_data.ticker, selected_timeframe, f_res_above, f_sup_below)
        print(
            f"Completed sup-res execution in {time.perf_counter() - now_supres} seconds"
        )
        print(f"Completed execution in total {time.perf_counter() - perf} seconds")
        return self.fig.show(id="the_graph", config={"displaylogo": False})

    def fibonacci_pricelevels(
        self, 
        high_price, low_price
    ) -> tuple[list[float], list[float]]:
        """
        Uptrend Fibonacci Retracement Formula =>
        Fibonacci Price Level = High Price - (High Price - Low Price)*Fibonacci Level
        :param high_price: High price for the period
        :param low_price: Low price for the period
        """
        for multiplier in self.fibonacci_multipliers:
            retracement_levels_uptrend = (
                low_price + (high_price - low_price) * multiplier
            )
            self.fibonacci_uptrend.append(retracement_levels_uptrend)
            retracement_levels_downtrend = (
                high_price - (high_price - low_price) * multiplier
            )
            self.fibonacci_downtrend.append(retracement_levels_downtrend)
        return self.fibonacci_uptrend, self.fibonacci_downtrend

    def sensitivity(
        self,
        sens=2
    ) -> tuple[list, list]:
        """
        Find the support and resistance levels for a given asset.
        sensitivity:1 is recommended for daily charts or high frequency trade scalping.
        :param sens: sensitivity parameter default:2, level of detail 1-2-3 can be given to function
        """
        for sens_row in range(3, len(self.df) - 1):
            if support_resistance.support(self.df, sens_row, 3, sens):
                self.support_list.append((sens_row, self.df.low[sens_row]))
            if support_resistance.resistance(self.df, sens_row, 3, sens):
                self.resistance_list.append((sens_row, self.df.high[sens_row]))
        return self.support_list, self.resistance_list

    def chart_lines(self):
        """
        Check if the support and resistance lines are above or below the latest close price.
        """
        # Find support and resistance levels
        # Check if the support is below the latest close. If it is, it is appending it to the list
        # self.support_below. If it isn't, it is appending it to the list resistance_below.
        all_support_list = tuple(map(lambda sup1: sup1[1], self.support_list))
        all_resistance_list = tuple(map(lambda res1: res1[1], self.resistance_list))
        print(all_support_list, all_resistance_list)
        latest_close = self.df["close"].iloc[-1]
        for support_line in all_resistance_list:  # Find closes
            if support_line < latest_close:
                self.support_below.append(support_line)
            else:
                self.resistance_below.append(support_line)
        if len(self.support_below) == 0:
            self.support_below.append(min(self.df.low))
        # Check if the price is above the latest close price. If it is, it is appending it to the
        # self.resistance_above list. If it is not, it is appending it to the self.self.support_above list.
        for resistance_line in all_resistance_list:
            if resistance_line > latest_close:
                self.resistance_above.append(resistance_line)
            else:
                self.support_above.append(resistance_line)
        if len(self.resistance_above) == 0:
            self.resistance_above.append(max(self.df.high))
        return self.fibonacci_pricelevels(max(self.resistance_above), min(self.support_below))

    def candlestick_patterns(self) -> list:
        """
        Takes in a dataframe and returns a list of candlestick patterns found in the dataframe then returns
        pattern list.
        """
        from candlestick import candlestick as cd

        all_patterns = [
            cd.inverted_hammer,
            cd.hammer,
            cd.doji,
            cd.bearish_harami,
            cd.bearish_engulfing,
            cd.bullish_harami,
            cd.bullish_engulfing,
            cd.dark_cloud_cover,
            cd.dragonfly_doji,
            cd.hanging_man,
            cd.gravestone_doji,
            cd.morning_star,
            cd.morning_star_doji,
            cd.piercing_pattern,
            cd.star,
            cd.shooting_star,
        ]
        # Loop through the candlestick pattern functions
        for pattern in all_patterns:
            # Apply the candlestick pattern function to the data frame
            self.df = pattern(self.df)
        # Replace True values with 'pattern_found'
        self.df.replace({True: "pattern_found"}, inplace=True)

        def pattern_find_func(pattern_row) -> list:
            """
            The function takes in a dataframe and a list of column names. It then iterates through the
            list of column names and checks if the column name is in the dataframe. If it is, it adds
            the column name to a list and adds the date of the match to another list.
            """
            t = 0
            pattern_find = [col for col in df.columns]
            for pattern_f in pattern_row:
                if pattern_f == "pattern_found":
                    self.pattern_list.append(
                        (pattern_find[t], pattern_row["date"].strftime("%b-%d-%y"))
                    )  # pattern, date
                t += 1
            return self.pattern_list

        return self.df.iloc[-3:-30:-1].apply(pattern_find_func, axis=1)

    def legend_candle_patterns(self) -> None:
        """
        The function takes the list of candlestick patterns and adds them to the chart as a legend text.
        """
        self.fig.add_trace(
            go.Scatter(
                y=[self.support_list[0]],
                name="----------------------------------------",
                mode="markers",
                marker=dict(color=self.legend_color, size=14),
            )
        )
        self.fig.add_trace(
            go.Scatter(
                y=[self.support_list[0]],
                name="Latest Candlestick Patterns",
                mode="markers",
                marker=dict(color=self.legend_color, size=14),
            )
        )
        for pat1, count in enumerate(self.pattern_list):  # Candlestick patterns
            self.fig.add_trace(
                go.Scatter(
                    y=[self.support_list[0]],
                    name=f"{self.pattern_list[pat1][1]} : {str(self.pattern_list[pat1][0]).capitalize()}",
                    mode="lines",
                    marker=dict(color=self.legend_color, size=10),
                )
            )

    def create_candlestick_plot(self) -> None:
        """
        Creates a candlestick plot using the dataframe df, and adds it to the figure.
        """
        self.fig.add_trace(
            go.Candlestick(
                x=self.df["date"][:-1].dt.strftime(self.x_date),
                name="Candlestick",
                text=self.df["date"].dt.strftime(self.x_date),
                open=self.df["open"],
                high=self.df["high"],
                low=self.df["low"],
                close=self.df["close"],
            ),
            row=1,
            col=1,
        )

    def draw_support(self) -> None:
        """
        Draws the support lines and adds annotations to the chart.
        """
        for s in range(len(self.support_list)):
            # Support lines
            self.fig.add_shape(
                type="line",
                x0=self.support_list[s][0] - 1,
                y0=self.support_list[s][1],
                x1=len(self.df) + 25,
                y1=self.support_list[s][1],
                line=dict(color=self.support_line_color, width=2),
            )
            # Support annotations
            self.fig.add_annotation(
                x=len(self.df) + 7,
                y=self.support_list[s][1],
                text=str(self.support_list[s][1]),
                font=dict(size=15, color=self.support_line_color),
            )

    def draw_resistance(self) -> None:
        """
        Draws the resistance lines and adds annotations to the chart.
        """
        for r in range(len(self.resistance_list)):
            # Resistance lines
            self.fig.add_shape(
                type="line",
                x0=self.resistance_list[r][0] - 1,
                y0=self.resistance_list[r][1],
                x1=len(self.df) + 25,
                y1=self.resistance_list[r][1],
                line=dict(color=self.resistance_line_color, width=1),
            )
            # Resistance annotations
            self.fig.add_annotation(
                x=len(self.df) + 20,
                y=self.resistance_list[r][1],
                text=str(self.resistance_list[r][1]),
                font=dict(size=15, color=self.resistance_line_color),
            )

        self.legend_support_resistance_values()
        self.text_and_indicators()
        self.legend_fibonacci()
        # Candle patterns for HTF
        if self.selected_timeframe in self.historical_hightimeframe:
            self.legend_candle_patterns()

    def chart_updates(self) -> None:
        """
        Updates the chart's layout, background color, chart color, legend color, and margin.
        """
        self.fig.update_layout(
            title=str(
                f"{historical_data.ticker} {self.selected_timeframe.upper()} Chart"
            ),
            hovermode="x",
            dragmode="zoom",
            paper_bgcolor=self.background_color,
            plot_bgcolor=self.chart_color,
            xaxis_rangeslider_visible=False,
            legend=dict(bgcolor=self.legend_color, font=dict(size=11)),
            margin=dict(t=30, l=0, b=0, r=0),
        )
        self.fig.update_xaxes(showspikes=True, spikecolor="green", spikethickness=2)
        self.fig.update_yaxes(showspikes=True, spikecolor="green", spikethickness=2)

    def save(self, candle_count):
        """
        Saves the image and html file of the plotly chart, then it tweets the image and text
        """

        if not os.path.exists("../images"):
            os.mkdir("../images")

        image = (
            f"../images/"
            f"{self.df['date'].dt.strftime('%b-%d-%y')[candle_count]}"
            f"{historical_data.ticker + '-' + self.selected_timeframe}.jpeg"
        )
        self.fig.write_image(image, width=1920, height=1080)  # Save image for tweet
        self.fig.write_html(
            f"../images/"
            f"{self.df['date'].dt.strftime('%b-%d-%y')[candle_count]}{historical_data.ticker + self.selected_timeframe}.html",
            full_html=False,
            include_plotlyjs="cdn",
        )
        with open('../templates/all_levels.html', 'a') as f:
            f.write('''<button class="accordion">''' + historical_data.ticker + '''</button>''')
            f.write('''<div class="panel">''')
            f.write(self.fig.to_html(full_html=False, include_plotlyjs='cdn'))
            f.write('''</div>''')

        text_image = (
            f"#{historical_data.ticker} "
            f"{self.selected_timeframe} Support and resistance levels \n "
            f"{self.df['date'].dt.strftime('%b-%d-%Y')[candle_count]}"
        )


if __name__ == "__main__":
    file_name = historical_data.user_ticker.file_name
    file_name_mtf = historical_data.user_ticker_mtf.file_name
    file_name_ltf = historical_data.user_ticker_ltf.file_name

    try:
        try:
            os.remove('../templates/all_levels.html')
        except OSError:
            pass
        perf = time.perf_counter()
        if os.path.isfile(file_name):  # Check .csv file exists
            print(f"{file_name} downloaded and created.")
            htf_supres = Supres()
            mtf_supres = Supres()
            ltf_supres = Supres()
            htf_supres.main(file_name, historical_data.time_frame)
            mtf_supres.main(file_name_mtf, historical_data.med_time_frame)
            ltf_supres.main(file_name_ltf, historical_data.low_time_frame)

            print("Data analysis is done. Browser opening.")

            os.remove(file_name)  # remove the .csv file
            print(f"{file_name} file deleted.")

            os.remove(file_name_mtf)  # remove the .csv file
            print(f"{file_name_mtf} file deleted.")

            os.remove(file_name_ltf)  # remove the .csv file
            print(f"{file_name_ltf} file deleted.")


        else:
            raise print(
                "One or more issues caused the download to fail. "
                "Make sure you typed the filename correctly."
            )
    except KeyError:
        os.remove(file_name)
        raise KeyError("Key error, algorithm issue")

def get_near_sr(supres: Supres, sensitivty: float):
    supports = supres