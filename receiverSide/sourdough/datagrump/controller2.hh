#ifndef CONTROLLER_HH
#define CONTROLLER_HH

#include <stdint.h>

/* Flow controller interface */

class Controller
{
private:
  bool debug_; /* Enables debugging output */

  uint64_t cur_pkt_count; /* Packets received in current tick */
  uint64_t last_tick_time; /* Last tick processed by the estimator */
  double throughput; /* Throughput estimate (1/ms) */
  int ticks_higher, ticks_lower; /* Bias counts */

  /* Update throughput estimate with information from the last tick */
  void update_estimate(uint64_t cur_time, uint64_t recent_delay);

public:
  /* Public interface for the flow controller */
  /* You can change these if you prefer, but will need to change
     the call site as well (in datagrump-sender.cc) */

  /* Default constructor */
  Controller( const bool debug );

  /* Get current window size, in packets */
  unsigned int window_size( void );

  /* A packet was sent */
  void packet_was_sent( const uint64_t sequence_number,
			const uint64_t send_timestamp );

  /* An ack was received */
  void ack_received( const uint64_t sequence_number_acked,
		     const uint64_t send_timestamp_acked,
		     const uint64_t recv_timestamp_acked,
		     const uint64_t timestamp_ack_received );

  /* How long to wait if there are no acks before sending one more packet */
  unsigned int timeout_ms( void );
};

#endif
