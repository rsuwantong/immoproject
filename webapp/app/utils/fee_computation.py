def compute_fee(agency_fees, price_keuros):
    [x*price_keuros if x is not None else y for x,y in zip(agency_fees["agency_rate"], agency_fees["agency_fee_min_keuros"])]