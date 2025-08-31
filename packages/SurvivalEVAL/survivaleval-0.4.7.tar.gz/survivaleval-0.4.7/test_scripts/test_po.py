import datetime
import numpy as np
from dataclasses import field
from tqdm import trange

from SurvivalEVAL.NonparametricEstimator.SingleEvent import KaplanMeier, KaplanMeierArea


class KaplanMeierAreaOld(KaplanMeier):
    area_times: np.array = field(init=False)
    area_probabilities: np.array = field(init=False)
    area: np.array = field(init=False)

    def __post_init__(self, event_times, event_indicators):
        super().__post_init__(event_times, event_indicators)
        area_probabilities = np.append(1, self.survival_probabilities)
        area_times = np.append(0, self.survival_times)
        if self.survival_probabilities[-1] != 0:
            slope = (area_probabilities[-1] - 1) / area_times[-1]
            zero_survival = -1 / slope
            area_times = np.append(area_times, zero_survival)
            area_probabilities = np.append(area_probabilities, 0)

        area_diff = np.diff(area_times, 1)
        area_subs = area_diff * area_probabilities[0:-1]
        area_subs[-1] = area_subs[-1] / 2
        area = np.flip(np.flip(area_subs).cumsum())
        # area = np.flip(np.flip(area_diff * area_probabilities[0:-1]).cumsum())

        self.area_times = np.append(area_times, np.inf)
        self.area_probabilities = area_probabilities
        self.area = np.append(area, 0)

    def best_guess(self, censor_times: np.array):
        surv_prob = self.predict(censor_times)
        censor_indexes = np.digitize(censor_times, self.area_times)
        censor_indexes = np.where(
            censor_indexes == self.area_times.size + 1,
            censor_indexes - 1,
            censor_indexes,
        )
        censor_area = (
            self.area_times[censor_indexes] - censor_times
        ) * self.area_probabilities[censor_indexes - 1]
        censor_area += self.area[censor_indexes]
        return censor_times + censor_area / surv_prob


def km_mean(
        times: np.ndarray,
        survival_probabilities: np.ndarray
) -> float:
    """
    Calculate the mean of the Kaplan-Meier curve.

    Parameters
    ----------
    times: np.ndarray, shape = (n_samples, )
        Survival times for KM curve of the testing samples
    survival_probabilities: np.ndarray, shape = (n_samples, )
        Survival probabilities for KM curve of the testing samples

    Returns
    -------
    The mean of the Kaplan-Meier curve.
    """
    # calculate the area under the curve for each interval
    area_probabilities = np.append(1, survival_probabilities)
    area_times = np.append(0, times)
    km_linear_zero = -1 / ((area_probabilities[-1] - 1) / area_times[-1])
    if survival_probabilities[-1] != 0:
        area_times = np.append(area_times, km_linear_zero)
        area_probabilities = np.append(area_probabilities, 0)
    area_diff = np.diff(area_times, 1)
    # we are using trap rule
    # average_probabilities = (area_probabilities[0:-1] + area_probabilities[1:]) / 2
    # area = np.flip(np.flip(area_diff * average_probabilities).cumsum())
    # area = np.append(area, 0)
    area_subs = area_diff * area_probabilities[0:-1]
    area_subs[-1] = area_subs[-1] / 2
    area = np.flip(np.flip(area_subs).cumsum())

    # calculate the mean
    surv_prob = get_prob_at_zero(times, survival_probabilities)
    return area[0] / surv_prob


def get_prob_at_zero(
        times: np.ndarray,
        survival_probabilities: np.ndarray
) -> float:
    """
    Get the survival probability at time 0. Note that this function doesn't consider the interpolation.

    Parameters
    ----------
    times: np.ndarray, shape = (n_samples, )
        Survival times for KM curve of the testing samples
    survival_probabilities: np.ndarray, shape = (n_samples, )
        Survival probabilities for KM curve of the testing samples

    Returns
    -------
    The survival probability at time 0.
    """
    probability_index = np.digitize(0, times)
    probability = np.append(1, survival_probabilities)[probability_index]

    return probability


def PO_old(t_train, e_train, t_test, e_test, n_train, n_test, verbose):
    # ICML version
    start_time = datetime.datetime.now()
    km_model = KaplanMeierArea(t_train, e_train)
    pause_time_1 = datetime.datetime.now()
    print("Time elapsed for KM: ", pause_time_1 - start_time)
    best_guesses = np.empty(n_test)
    pasue_time_2 = datetime.datetime.now()
    sub_expect_time = km_model._compute_best_guess(0)
    pasue_time_3 = datetime.datetime.now()
    print("Time elapsed for sub_expect_time: ", pasue_time_3 - pasue_time_2)
    total_event_time = np.empty(n_train + 1)
    total_event_indicator = np.empty(n_train + 1)
    total_event_time[0:-1] = t_train
    total_event_indicator[0:-1] = e_train
    build_km_time = 0
    cal_mean_time = 0
    for i in trange(n_test, desc="Calculating surrogate times for MAE-PO", disable=not verbose):
        if e_test[i] == 1:
            best_guesses[i] = t_test[i]
        else:
            total_event_time[-1] = t_test[i]
            total_event_indicator[-1] = 0
            pasue_time_4 = datetime.datetime.now()
            total_km_model = KaplanMeierArea(total_event_time, total_event_indicator)
            pasue_time_5 = datetime.datetime.now()
            total_expect_time = total_km_model._compute_best_guess(0) # TODO: check why best_guess and _best_guess_revise give different results
            pasue_time_6 = datetime.datetime.now()
            best_guesses[i] = (n_train + 1) * total_expect_time - n_train * sub_expect_time
            build_km_time += (pasue_time_5 - pasue_time_4).total_seconds()
            cal_mean_time += (pasue_time_6 - pasue_time_5).total_seconds()

    print("Time elapsed for build_km_time: ", build_km_time)
    print("Time elapsed for cal_mean_time: ", cal_mean_time)
    return best_guesses

def PO(t_train, e_train, t_test, e_test, n_train, n_test, verbose):
    # the current survivalEVAL version, but slightly slower
    start_time = datetime.datetime.now()
    km_model = KaplanMeierArea(t_train, e_train)
    pause_time_1 = datetime.datetime.now()
    print("Time elapsed for KM: ", pause_time_1 - start_time)
    best_guesses = np.empty(n_test)
    pasue_time_2 = datetime.datetime.now()
    sub_expect_time = km_model.mean
    pasue_time_3 = datetime.datetime.now()
    print("Time elapsed for sub_expect_time: ", pasue_time_3 - pasue_time_2)
    total_event_time = np.empty(n_train + 1)
    total_event_indicator = np.empty(n_train + 1)
    total_event_time[0:-1] = t_train
    total_event_indicator[0:-1] = e_train
    build_km_time = 0
    cal_mean_time = 0
    for i in trange(n_test, desc="Calculating surrogate times for MAE-PO", disable=not verbose):
        if e_test[i] == 1:
            best_guesses[i] = t_test[i]
        else:
            total_event_time[-1] = t_test[i]
            total_event_indicator[-1] = 0
            pasue_time_4 = datetime.datetime.now()
            total_km_model = KaplanMeierArea(total_event_time, total_event_indicator)
            pasue_time_5 = datetime.datetime.now()
            total_expect_time = total_km_model.mean
            pasue_time_6 = datetime.datetime.now()
            best_guesses[i] = (n_train + 1) * total_expect_time - n_train * sub_expect_time
            build_km_time += (pasue_time_5 - pasue_time_4).total_seconds()
            cal_mean_time += (pasue_time_6 - pasue_time_5).total_seconds()

    print("Time elapsed for build_km_time: ", build_km_time)
    print("Time elapsed for cal_mean_time: ", cal_mean_time)
    return best_guesses


def PO_fast(t_train, e_train, t_test, e_test, n_train, n_test, verbose):
    # the current survivalEVAL version, with same speed, but slightly different results (using step func for area)
    start_time = datetime.datetime.now()
    km_model = KaplanMeierArea(t_train, e_train)
    pause_time_1 = datetime.datetime.now()
    print("Time elapsed for KM: ", pause_time_1 - start_time)
    best_guesses = np.empty(n_test)
    pasue_time_2 = datetime.datetime.now()
    # sub_expect_time = km_model.mean
    sub_expect_time = km_mean(km_model.survival_times, km_model.survival_probabilities)
    pasue_time_3 = datetime.datetime.now()
    print("Time elapsed for sub_expect_time: ", pasue_time_3 - pasue_time_2)
    # build_km_time = 0
    # cal_mean_time = 0
    for i in trange(n_test, desc="Calculating surrogate times for MAE-PO", disable=not verbose):
        if e_test[i] == 1:
            best_guesses[i] = t_test[i]
        else:
            pasue_time_4 = datetime.datetime.now()
            total_times, survival_probabilities = insert_km(km_model.survival_times.copy(), km_model.events.copy(), km_model.population_count.copy(),
                                                  t_test[i], 0)
            total_expect_time = km_mean(total_times, survival_probabilities)
            # total_expect_time = get_km_mean_total(km_model.survival_times.copy(), km_model.events.copy(), km_model.population_count.copy(),
            #                                       t_test[i], e_test[i])
            pasue_time_6 = datetime.datetime.now()
            best_guesses[i] = (n_train + 1) * total_expect_time - n_train * sub_expect_time
            # cal_mean_time += (pasue_time_6 - pasue_time_4).total_seconds()
    end_time = datetime.datetime.now()
    print("Time elapsed for PO_fast: ", end_time - start_time)
    return best_guesses


def PO_more_fast(t_train, e_train, t_test, e_test, n_train, n_test, verbose):
    # the fastest way, using dynamic programming
    start_time = datetime.datetime.now()
    km_model = KaplanMeierArea(t_train, e_train)
    sub_expect_time = km_mean(km_model.survival_times.copy(), km_model.survival_probabilities.copy())
    # sub_expect_time = km_model.mean

    events, population_counts = km_model.events.copy(), km_model.population_count.copy()
    times = km_model.survival_times.copy()

    unique_idx = np.where(events != 0)[0]
    if unique_idx[-1] != len(events) - 1:
        unique_idx = np.append(unique_idx, len(events) - 1)
    times = times[unique_idx]
    population_counts = population_counts[unique_idx]
    events = events[unique_idx]

    multiplier = 1 - events / population_counts
    multiplier_total = 1 - events / (population_counts + 1)
    best_guesses = t_test.copy().astype(float)

    # censor_times = t_test[e_test == 0]
    # censor_times = np.sort(censor_times)
    # insert_index = np.searchsorted(times, censor_times)
    #
    # for i in range(len(np.unique(insert_index)))

    for i in trange(n_test, desc="Calculating surrogate times for MAE-PO", disable=not verbose):
        if e_test[i] != 1:
            # TODO: no outliers
            total_multiplier = multiplier.copy()
            insert_index = np.searchsorted(times, t_test[i])
            total_multiplier[:insert_index+1] = multiplier_total[:insert_index+1]
            survival_probabilities = np.cumprod(total_multiplier)
            if insert_index == len(times):
                times_addition = np.append(times, t_test[i])
                survival_probabilities_addition = np.append(survival_probabilities, survival_probabilities[-1])
                total_expect_time = km_mean(times_addition, survival_probabilities_addition)
            else:
                total_expect_time = km_mean(times, survival_probabilities)
            best_guesses[i] = (n_train + 1) * total_expect_time - n_train * sub_expect_time
            # cal_mean_time += (pasue_time_6 - pasue_time_4).total_seconds()
    end_time = datetime.datetime.now()
    print("Time elapsed for PO_more_fast: ", end_time - start_time)
    return best_guesses


def insert_km(
        survival_times: np.ndarray,
        event_count: np.ndarray,
        as_risk_count: np.ndarray,
        new_t: float,
        new_e: int
) -> (np.ndarray, np.ndarray):
    # Find the index where new_t should be inserted
    insert_index = np.searchsorted(survival_times, new_t)

    # Check if new_t is already at the found index
    if insert_index < len(survival_times) and survival_times[insert_index] == new_t:
        # If new_t is already in the array, increment the event count
        event_count[insert_index] += new_e
        as_risk_count[:insert_index + 1] += 1
    else:
        # Insert new_t into
        survival_times = np.insert(survival_times, insert_index, new_t)
        event_count = np.insert(event_count, insert_index, new_e)
        if insert_index == survival_times.size - 1:
            as_risk_count = np.insert(as_risk_count, insert_index, 0)
        else:
            as_risk_count = np.insert(as_risk_count, insert_index, as_risk_count[insert_index])
        as_risk_count[:insert_index + 1] += 1

    event_ratios = 1 - event_count / as_risk_count
    survival_probabilities = np.cumprod(event_ratios)

    return survival_times, survival_probabilities


def margin_0(t_train, e_train, t_test, e_test, n_train, n_test, verbose):
    # the version that Haider created, and changing the last step to triangle
    start_time = datetime.datetime.now()
    km_model = KaplanMeierAreaOld(t_train, e_train)
    censor_times = t_test[e_test == 0]
    best_guesses = np.empty(n_test)
    best_guesses[e_test == 0] = km_model.best_guess(censor_times)
    best_guesses[e_test == 1] = t_test[e_test == 1]
    end_time = datetime.datetime.now()
    print("Time elapsed for margin_0: ", end_time - start_time)
    return best_guesses


def margin_1(t_train, e_train, t_test, e_test, n_train, n_test, verbose):
    # the version that used in the ICML paper
    start_time = datetime.datetime.now()
    km_model = KaplanMeierArea(t_train, e_train)
    censor_times = t_test[e_test == 0]
    best_guesses = np.empty(n_test)
    best_guesses[e_test == 0] = km_model.best_guess_revise(censor_times)
    best_guesses[e_test == 1] = t_test[e_test == 1]
    end_time = datetime.datetime.now()
    print("Time elapsed for margin_1: ", end_time - start_time)
    return best_guesses

def margin_2(t_train, e_train, t_test, e_test, n_train, n_test, verbose):
    # the new version, using trapezoid rule
    start_time = datetime.datetime.now()
    km_model = KaplanMeierArea(t_train, e_train)
    censor_times = t_test[e_test == 0]
    best_guesses = np.empty(n_test)
    best_guesses[e_test == 0] = km_model.best_guess(censor_times)
    best_guesses[e_test == 1] = t_test[e_test == 1]
    end_time = datetime.datetime.now()
    print("Time elapsed for margin_2: ", end_time - start_time)
    return best_guesses


if __name__ == "__main__":
    # get running times of each part of the code

    # first randomly generate some data
    verbose = True

    # test case #1
    # n_train = 100000
    # n_test = int(0.1 * n_train)
    # np.random.seed(10)
    #
    # # generate event times and event indicators
    # t_train = np.round(np.random.uniform(0, 5, n_train), 2)
    # e_train = np.random.binomial(1, 0.3, n_train)
    #
    # t_test = np.round(np.random.uniform(0, 10, n_test), 2)
    # e_test = np.random.binomial(1, 0.3, n_test)

    # test case #2
    # t_train = np.array([0, 1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22,
    #                     26, 27, 28, 29, 30, 31, 32, 33, 34,  60, 61, 62, 63, 64, 65, 66, 67,
    #                     74, 75, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93,
    #                     98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111,
    #                     117, 118, 119, 120, 120, 120, 121, 121, 124, 125, 126, 127, 128, 129,
    #                     136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149,
    #                     155, 156, 157, 158, 159, 161, 182, 183, 186, 190, 191, 192, 192, 192,
    #                     193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 202, 203,
    #                     204, 202, 203, 204, 212, 213, 214, 215, 216, 217, 222, 223, 224])
    # e_train = np.array([1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0,
    #                     1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    #                     0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0,
    #                     0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
    #                     0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0,
    #                     1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0,
    #                     0, 0, 1, 1, 0, 0, 0, 0, 0, 0])
    # t_test = np.array([5, 10, 19, 31, 43, 59, 63, 75, 97, 113, 134, 151, 163, 176, 182, 195, 200, 210, 220, 250])
    # e_test = np.array([1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0])
    # n_train = t_train.size
    # n_test = t_test.size

    # test case #3
    t_train = np.load("../train_t.npy", allow_pickle=True)
    e_train = np.load("../train_e.npy", allow_pickle=True)
    t_test = np.load("../test_t.npy", allow_pickle=True)
    e_test = np.load("../test_e.npy", allow_pickle=True)
    n_train = t_train.size
    n_test = t_test.size

    # po0 = PO_old(t_train, e_train, t_test, e_test, n_train, n_test, verbose)
    # po1 = PO(t_train, e_train, t_test, e_test, n_train, n_test, verbose)
    po2 = PO_fast(t_train, e_train, t_test, e_test, n_train, n_test, verbose)
    # po3 = PO_more_fast(t_train, e_train, t_test, e_test, n_train, n_test, verbose)
    # print("Does the three PO methods give the same results? ", np.all(po1 == po2) and np.all(po1 == po3))
    # m0 = margin_0(t_train, e_train, t_test, e_test, n_train, n_test, verbose)
    # m1 = margin_1(t_train, e_train, t_test, e_test, n_train, n_test, verbose)
    # m2 = margin_2(t_train, e_train, t_test, e_test, n_train, n_test, verbose)
    # print("Does the three margin methods give the same results? ", np.all(m0 == m1) and np.all(m0 == m2))
