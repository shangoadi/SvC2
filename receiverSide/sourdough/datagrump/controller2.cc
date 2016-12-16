#include <algorithm>
#include <climits>
#include <stdio.h>

#include "controller.hh"
#include "timestamp.hh"

using namespace Network;

/* Default constructor */
Controller::Controller(const bool debug)
  : debug_(debug),
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

/* Get current window size, in packets */
unsigned int Controller::window_size(void)
{
  unsigned int the_window_size = (unsigned int)
    (throughput * (1.0 + BIAS_SCALE * (ticks_higher - ticks_lower)) * SAFE_DELAY);

  if (debug_) {
    fprintf(stderr, "At time %lu, return window_size = %d.\n",
	     timestamp(), the_window_size);
  }

  return the_window_size;
}

/* A packet was sent */
void Controller::packet_was_sent(
          const uint64_t sequence_number,
				  /* of the sent packet */
				  const uint64_t send_timestamp)
          /* in milliseconds */
{
  if (debug_) {
    fprintf(stderr, "At time %lu, sent packet %lu.\n",
	     send_timestamp, sequence_number);
  }

  update_estimate(send_timestamp, 0);
}

/* An ack was received */
void Controller::ack_received(const uint64_t sequence_number_acked,
                              /* what sequence number was acknowledged */
                              const uint64_t send_timestamp_acked,
                              /* when the acknowledged packet was sent */
                              const uint64_t recv_timestamp_acked,
                              /* when the acknowledged packet was received */
                              const uint64_t timestamp_ack_received)
                              /* when the ack was received (by sender) */
{
//  if (debug_) {
    fprintf(stderr, "At time %lu, received ACK for packet %lu",
	    timestamp_ack_received, sequence_number_acked);

    fprintf(stderr, " (sent %lu, received %lu by receiver's clock).\n",
	    send_timestamp_acked, recv_timestamp_acked);

    fprintf(stderr, "  delay=%lu, rtt=%lu\n",
      recv_timestamp_acked - send_timestamp_acked,
      timestamp_ack_received - send_timestamp_acked);
 // }

  /* Calculate RTT and (possibly inaccurate) one-way delay, 2/rtt is an alternative */
  uint64_t rtt = timestamp_ack_received - send_timestamp_acked;
  uint64_t inaccurate_delay = recv_timestamp_acked > send_timestamp_acked ?
    recv_timestamp_acked - send_timestamp_acked : 252525;
  inaccurate_delay = std::min(inaccurate_delay, rtt);

  update_estimate(timestamp_ack_received, inaccurate_delay);

  /* It's crucial that we increment the received count after updating the estimate */
  cur_pkt_count++;
}

/* How long to wait if there are no acks before sending one more packet */
unsigned int Controller::timeout_ms(void)
{
  return TIMEOUT; /* timeout of 100 ms */
}

