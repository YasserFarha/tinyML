#!/usr/bin/env python
import tensorflow as tf
import sys, time

CSIZE=10000
# Create a Variable, that will be initialized to the scalar value 0.
state = tf.Variable([0 for x in range(CSIZE)], name="counter")

MAX=10000

# Create an Op to add one to `state`.
one = tf.constant([1 for x in range(CSIZE)])
new_value = tf.add(state, one)
update = tf.assign(state, new_value)

# Variables must be initialized by running an `init` Op after having

# launched the graph.  We first have to add the `init` Op to the graph.
init_op = tf.initialize_all_variables()

if __name__ == '__main__' :
    # Launch the graph and run the ops.
    with tf.Session() as sess:
        # Run the 'init' op
        sess.run(init_op)
        # Print the initial value of 'state'
        print sess.run(state)
        # Run the op that updates 'state' and print 'state'.
        print "starting ..."
        t0 = time.time()
        for _ in range(int(sys.argv[1]) if len(sys.argv) > 1 else MAX):
            sess.run(update)

        print str(sess.run(state)) + str(time.time() - t0)

        counters = [0 for x in range(CSIZE)]
        print "starting ..."
        t0 = time.time()
        for _ in range(int(sys.argv[1]) if len(sys.argv) > 1 else MAX):
            for x in range(0, len(counters)) :
                counters[x]+=1

        print str(counters[0]) + ", " +  str(time.time() - t0)
