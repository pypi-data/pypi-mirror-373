Welcome to Juham™ - Juha's Ultimate Home Automation Masterpiece
================================================================

Project Description
-------------------

This package extends the ``juham_core`` package, providing home automation building blocks that address most common needs. It consists of two main sub-modules:

``automation``:
- **spothintafi**: Acquires electricity prices in Finland.
- **watercirculator**: Automates a water circulator pump based on hot water temperature and motion detection.
- **heatingoptimizer**: Controls hot water radiators based on temperature sensors and electricity price data.
- **energycostcalculator**: Monitors power consumption and electricity prices, and computes the energy balance in euros.
- **energybalancer**: Handles real-time energy balancing and net billing.

``ts``:
- This folder contains time series recorders that listen for Juham™ topics and store the data in a time series database for later inspection.

Project Status
--------------

**Current State**: **Pre-Alpha (Status 2)**

All classes have been tested to some extent, and no known bugs have been reported. However, the code still requires work in terms of design and robustness. For example, electricity prices are currently hard-coded to use euros, but this should be configurable to support multiple currencies.


Features
--------

**HeatingAutomater** listens to the power meter to compute the net energy balance.

  .. image:: _static/images/juham_powermeter.png
     :alt: Powermeter
     :width: 400px

  Powermeter is needed to measure the real-time energy consumption


**Energy Revenue** is computed based on the electricity price and transmission costs. This is the total cost one has to pay for consuming energy.
  
  .. image:: _static/images/juham_energyrevenue.png
     :alt: Energy Revenue
     :width: 400px

  Energy revenue per hour and per day


**Real-time temperature** trends monitored by the **Shelly Plus Add-on** and **DS18B20** sensors
  
  .. image:: _static/images/juham_boilertemperatures.png
     :alt: Energy Revenue
     :width: 400px

  Temperature time series.


**Real-time humidity** trends monitored by the **Shelly Plus Add-on** and **DHT22** sensors
  
  .. image:: _static/images/juham_humiditysensors.png
     :alt: Energy Revenue
     :width: 400px

  Relative humidity time series.


  
**Utilization Optimization Index**: The Utilization Optimization Index predicts the optimal hours for energy consumption by factoring in electricity prices, temperature, and forecasts for wind and solar energy. It identifies the best times to activate heating systems. The cheapest hours within the current period may be skipped if the solar forecast predicts free electricity in the next period.period.

  .. image:: _static/images/juham_uoi.png
     :alt: Power Plan
     :width: 400px

  UOI cast for heating the primary and sun pre-heating boilers for two types of solar panels and boilers: electric-based panels and solar thermal panels, which use water circulation. The primary one is electrically heated, while the secondary ‘pre-heating’ boiler is heated by the hot water from the solar thermal panels, or by electricity when there's a positive energy balance.


**Power Plan** is computed for the next 12 hours based on the electricity price and solar energy forecast. If no solar energy is available, the power plan determines power consumption, e.g., when the hot water radiators are enabled.

  .. image:: _static/images/juham_powerplan.png
     :alt: Power Plan
     :width: 400px

  Powerplan optimizing consumers to use the cheapest hours


**Energy Balancer**: When the energy balance is positive (e.g., when solar panels produce more energy than is currently being consumed), the energy balancer is activated. It monitors the energy balance in 15-minute (or one-hour) intervals and computes when a consumer with a specific power demand should be activated to consume all the energy produced so far.

  .. image:: _static/images/juham_automation_energybalancer.png
     :alt: Energy Balancer
     :width: 400px

  Energy balancer activating consumers based on the actual real-time net energy


**Power Diagnosis**: All controlled relays are monitored to ensure their correct operation. This ensures that relays are enabled according to the power plan and energy balancer commands.

  .. image:: _static/images/juham_automation_relays.png
     :alt: Relays
     :width: 400px

  The operation of the relays for diagnosis.
