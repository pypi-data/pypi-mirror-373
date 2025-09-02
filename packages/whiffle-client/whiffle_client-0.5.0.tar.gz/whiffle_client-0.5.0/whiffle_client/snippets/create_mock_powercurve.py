import numpy as np


def cp_to_power(wind_speed, power_coefficient, radius, reference_density=1.225):
    return (
        0.5
        * power_coefficient
        * np.pi
        * radius**2.0
        * reference_density
        * wind_speed**3.0
    )


def ct_to_thrust(wind_speed, thrust, radius, reference_density=1.225):
    return 0.5 * thrust * np.pi * radius**2.0 * reference_density * wind_speed**2.0


def create_mock_design_curves(
    name,
    hub_height,
    rotor_diameter,  # [mm]
    rated_power,  # [W]
    rated_wind_speed=11,  # [m/s]
    cutin_wind_speed=4,  # [m/s]
    cutout_wind_speed=24,  # [m/s]
    reference_density=1.225,  # [kg/m^3]
    reference_turbulence_intensity=0.08,  # [-]
):
    reference_windspeed = np.arange(cutin_wind_speed, cutout_wind_speed + 0.5, 0.5)

    # Compute power
    power = np.minimum(
        cp_to_power(reference_windspeed, 0.45, rotor_diameter / 2, reference_density),
        rated_power,
    )
    # NOTE: it might reach rated power before rated_wind_speed ("v164_9500" example)
    # https://www.thewindpower.net/turbine_en_1476_vestas_v164-9500.php
    power[reference_windspeed >= rated_wind_speed] = rated_power

    # Compute thrust_coefficient
    thrust = ct_to_thrust(
        reference_windspeed, 0.9, rotor_diameter / 2, reference_density
    )
    before_rated_wind_speed = rated_wind_speed - 1
    max_thrust = thrust[reference_windspeed == before_rated_wind_speed]
    windspeed_mask = reference_windspeed > before_rated_wind_speed
    thrust[windspeed_mask] = max_thrust * np.maximum(
        0.1,
        (
            1
            - (reference_windspeed[windspeed_mask] - before_rated_wind_speed)
            / (cutout_wind_speed - before_rated_wind_speed)
        ),
    )

    thrust_coefficient = thrust / ct_to_thrust(
        reference_windspeed, 1, rotor_diameter / 2, reference_density
    )

    return {
        "name": name,
        "hub_height": hub_height,
        "rotor_diameter": rotor_diameter,
        "rated_power": rated_power,  # [W]
        "reference_density": reference_density,
        "reference_turbulence_intensity": reference_turbulence_intensity,
        "reference_windspeed": reference_windspeed.round(4).tolist(),
        "thrust_coefficient": thrust_coefficient.round(4).tolist(),
        "power": power.round(4).tolist(),
        "public": False,  # Expose turbine to other users
    }
