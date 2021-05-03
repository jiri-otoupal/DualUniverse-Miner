#
#      @@@  @@@@@@  @@@@@@@  @@@  @@@ @@@@@@@@ @@@
#      @@! @@!  @@@ @@!  @@@ @@!  @@@ @@!      @@!
#      !!@ @!@  !@! @!@  !@! @!@  !@! @!!!:!   @!!
#  .  .!!  !!:  !!! !!:  !!!  !: .:!  !!:      !!:
#  ::.::    : :. :  :: :  :     ::    : :: ::  : ::.: :
#

"""

Config

Modify only when you know ,what you are actually doing !

"""
import logging

# ---------------------------- Debug ------------------------------#

only_debug = False  # This results in not mining on request
dont_turn_debug = False  # This results in not rotating camera on request
dont_move = False  # This results in not moving on request

# ---------------------------- Debug ------------------------------#


# ------------------------- Bot Settings ---------------------------#
failsafe_timeout = 50  # Cycles in which timeout and do some movement to unblock
cloud = False
prediction_batch_size = 8
ore_threshold = 0.6  # Percent
full_auto = False  # Will increase mining radius ( SLOW )
model_to_use = "models/ores_a_v3_soft"  # Model to use for recognition
ore_list = ['bauxite', 'coal', 'hematite', 'quartz']  # whitelist of ores
log_level = logging.INFO  # Log leve ( Debug will show not only bot logs )
rotation_angle = 5  # degrees ( Smallest degree in sensitivity range is 2 )
forward_time = 1  # seconds

# Performance impact settings
#   Higher Number = Higher Impact on Performance and slower


circle_index_loop = 3  # Loops for circle modifying
circle_index_tempo = 0.1  # tempo in which to decrease panes of area that is searched
# ------------------------- Bot Settings ---------------------------#


logo = r"""                                                     
    @@@  @@@@@@  @@@@@@@  @@@  @@@ @@@@@@@@ @@@      
    @@! @@!  @@@ @@!  @@@ @@!  @@@ @@!      @@!      
    !!@ @!@  !@! @!@  !@! @!@  !@! @!!!:!   @!!      
.  .!!  !!:  !!! !!:  !!!  !: .:!  !!:      !!:      
::.::    : :. :  :: :  :     ::    : :: ::  : ::.: : 
                                                     """;
