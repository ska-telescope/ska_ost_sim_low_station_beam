from ska_ost_sim_low_station_beam.LowStation import LowStation

###########################################################
#
# Generate reference images for LowStation.plot_station_layout()
# without legend
#
###########################################################
station = LowStation("S8-1")
fig, _ = station.plot_station_layout()
fig.savefig("low_S8_1_station_layout.png")

###########################################################
#
# Generate reference images for LowStation.plot_station_layout()
# with legend
#
###########################################################
station = LowStation("S8-1")
fig, _ = station.plot_station_layout(
    plot_station_boundary=True,
    plot_principle_direction=True,
    plot_cardinal_direction=True,
)
fig.savefig("low_S8_1_station_layout_with_legend.png")
