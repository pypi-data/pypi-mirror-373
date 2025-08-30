// Copyright (c) 2025, UChicago Argonne, LLC
// All rights reserved. Full details of the terms by which this software is licensed can be found in LICENSE.md

#pragma once

template <typename T> struct by_time
{
    vector<pair<pair<second_t, second_t>, T>> values;

    // TODO: add a member to keep track of the currently found pair, based on the assumption that we will
    //       be looking up based on current_time, we shouldn't have to search all the way from the front
    //       i.e. auto e = find_if(m_prev_result, values.end(), in_bounds);

    void add_value(second_t low, second_t high, T value)
    {
        values.push_back({{low, high}, value});
        sort();
    }

    T get_value(const second_t q)
    {
        auto in_bounds = [=](const pair<pair<second_t, second_t>, T>& x) {
            return q >= x.first.first && q < x.first.second;
        };
        auto e = find_if(values.begin(), values.end(), in_bounds);
        if (e == values.end())
            THROW_EXCEPTION("Given time is outside range: " << q);
        return e->second;
    }

    // Make sure that entries are sorted by start_time
    void sort()
    {
        std::sort(values.begin(), values.end(),
                  [](const auto& a, const auto& b) { return a.first.first < b.first.first; });
    }

    // Standard sanity checking for non-overlapping or nonsense ranges
    bool sanity_check()
    {
        if (values.size() == 0)
            return true; // Can't be insane if we aint got no data

        for (const auto& [b, v] : values)
        {
            // Check that there are no ranges with high <= low
            if (b.first >= b.second)
                return false;
        }

        for (int i = 1; i < values.size(); ++i)
        {
            // Check that there is no overlap between consecutive ranges
            if (values[i - 1].first.second > values[i].first.first)
                return false;
        }

        return true;
    }

    // Standard sanity checking (as above) plus a check that the entire range between lo and high is covered by one
    // of the contained ranges
    bool sanity_check_range(second_t lo, second_t hi)
    {
        return size() == 0 || (sanity_check() && check_coverage(lo, hi));
    }

    bool check_coverage(second_t lo, second_t hi)
    {
        second_t current_lo = lo;
        for (const auto& [b, v] : values)
        {
            if (current_lo != b.first)
                return false;
            current_lo = b.second;
        }
        return current_lo == hi;
    }

    size_t size() { return values.size(); }
};