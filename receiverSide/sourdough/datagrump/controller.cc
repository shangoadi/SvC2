#include <iostream>

#include "controller.hh"
#include "timestamp.hh"

using namespace std;

/* Scales the bias measurement */
#define BIAS_SCALE (0.05 / 5)

/* Weight on new point when calculating EWMA */
#define EWMA_GAIN (0.2)

/* Length of a tick (ms) */
#define TICK_LEN (30)

/* Conversative specification of desired delay (ms) */
#define SAFE_DELAY (170)

#define TIMEOUT (100)

/* Default constructor */
Controller::Controller( const bool debug )
  : debug_( debug ),
    cur_pkt_count(0),
    last_tick_time(0),
    throughput(0.0),
    ticks_higher(0),
    ticks_lower(0)
{

}


void Controller::update_estimate(uint64_t cur_time, uint64_t recent_delay) {
  /* Have we stepped into a new tick? */
  if (cur_time - last_tick_time >= TICK_LEN) {
    /* If a real delay has been specified, then bound the throughput by 1/delay */
    double lower_bound = (recent_delay > 0) ? (1.0 / recent_delay) : 0.0;

    /* Update throughput */
    double recent_throughput = std::max(1.0 * cur_pkt_count / TICK_LEN, lower_bound);
    throughput = std::max((1.0 - EWMA_GAIN) * throughput + EWMA_GAIN * recent_throughput,
      lower_bound);

    /* Track sustained bias of the throughput estimate, higher OR lower */
    if (recent_throughput > throughput) {
      ticks_higher++;
      ticks_lower = 0;
    } else {
      ticks_lower++;
      ticks_higher = 0;
    }

    cur_pkt_count = 0;

    /* Round down to nearest tick length */
    last_tick_time = cur_time - (cur_time % TICK_LEN);
  }
}


/* Get current window size, in datagrams */
unsigned int Controller::window_size( void )
{
  unsigned int the_window_size = (unsigned int)
    (throughput * (1.0 + BIAS_SCALE * (ticks_higher - ticks_lower)) * SAFE_DELAY);


  if ( debug_ ) {
    cerr << "At time " << timestamp_ms()
	 << " window size is " << the_window_size << endl;
  }

  return the_window_size;

}

/* A datagram was sent */
void Controller::datagram_was_sent( const uint64_t sequence_number,
				    /* of the sent datagram */
				    const uint64_t send_timestamp )
                                    /* in milliseconds */
{
  /* Default: take no action */

  if ( debug_ ) {
    cerr << "At time " << send_timestamp
	 << " sent datagram " << sequence_number << endl;
  }

  update_estimate(send_timestamp, 0);
}

/* An ack was received */
void Controller::ack_received( const uint64_t sequence_number_acked,
			       /* what sequence number was acknowledged */
			       const uint64_t send_timestamp_acked,
			       /* when the acknowledged datagram was sent (sender's clock) */
			       const uint64_t recv_timestamp_acked,
			       /* when the acknowledged datagram was received (receiver's clock)*/
			       const uint64_t timestamp_ack_received )
                               /* when the ack was received (by sender) */
{
  /* Default: take no action */

  if ( debug_ ) {
    cerr << "At time " << timestamp_ack_received
	 << " received ack for datagram " << sequence_number_acked
	 << " (send @ time " << send_timestamp_acked
	 << ", received @ time " << recv_timestamp_acked << " by receiver's clock)"
	 << endl;
  }

  /* Calculate RTT and (possibly inaccurate) one-way delay, 2/rtt is an alternative */
  uint64_t rtt = timestamp_ack_received - send_timestamp_acked;
  uint64_t inaccurate_delay = recv_timestamp_acked > send_timestamp_acked ?
    recv_timestamp_acked - send_timestamp_acked : 252525;
  inaccurate_delay = std::min(inaccurate_delay, rtt);

  update_estimate(timestamp_ack_received, inaccurate_delay);

  /* It's crucial that we increment the received count after updating the estimate */
  cur_pkt_count++;

}

/* How long to wait (in milliseconds) if there are no acks
   before sending one more datagram */
unsigned int Controller::timeout_ms( void )
{
  return TIMEOUT; /* timeout of 100 ms */
}
