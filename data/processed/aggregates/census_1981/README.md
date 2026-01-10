# Household Indicator Definitions and Methodology

This document defines the indicators used to measure housing tenure, overcrowding, and amenities deprivation. All calculations are derived from the household dataset using the specified variable codes.

## 1. Core Parameters

The base population for all calculations is the total number of households.

* **Household Denominator:** `81sas100929`
* **Unit of Measurement:** Rates (0.0 to 1.0). 
    * *Note: Multiply results by 100 to obtain percentages.*

---

## 2. Housing and Transport Indicators

### Owner-Occupied Rate
The proportion of households that are owned by the residents (either outright or with a mortgage).
* **Numerator:** `81sas100967`
* **Formula:** > `owner_occupied_rate = 81sas100967 / 81sas100929`

### No-Car Households Rate
The proportion of households with no access to a car or van.
* **Numerator:** `81sas100949`
* **Formula:** > `no_car_rate = 81sas100949 / 81sas100929`

### Overcrowding Rate (> 1.5 persons per room)
The proportion of households where the occupancy density exceeds 1.5 persons per room.
* **Numerator:** `81sas100945`
* **Formula:** > `overcrowding_gt1_5_rate = 81sas100945 / 81sas100929`

---

## 3. Amenities Deprivation

These indicators identify households lacking basic sanitary facilities.

| Indicator Name | Numerator Code | Calculation Formula |
| :--- | :--- | :--- |
| **Lacks Bath/WC** | `81sas100932` | `81sas100932 / 81sas100929` |
| **No Inside Bath/WC** | `81sas100933` | `81sas100933 / 81sas100929` |
| **Any Amenities Deprivation** | `81sas100932 + 81sas100933` | `(81sas100932 + 81sas100933) / 81sas100929` |

---

## 4. Variable Reference Table

| Code | Label |
| :--- | :--- |
| **81sas100929** | Total Household Count (Denominator) |
| **81sas100967** | Tenure: Owner-occupied |
| **81sas100949** | Car Availability: None |
| **81sas100945** | Occupancy: More than 1.5 persons per room |
| **81sas100932** | Amenities: Lacks bath or WC |
| **81sas100933** | Amenities: No inside bath or WC |