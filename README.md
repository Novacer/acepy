# AcePy
Automatic Concurrent Execution in Python

**AcePy: Write simple single threaded Python code but get all the performance benefits of multithreading for free!**

Given a list of tasks,
AcePy finds the most optimal sequence to complete the tasks, executing them in parallel whenever possible.
AcePy accomplishes this automatically, and requires minimal refactoring of your code to work.

For example, suppose we are building a dashboard for an online shopping site. Suppose we need to do the following API/RPC calls to 
get all the relevant data to show.

1. ``getUserIdFromLoginData(data)``, which fetches the userId used thought our application.
2. ``getMembershipStatusFromUserId(id)``, which retrieves whether the user is a premium member in our online
shopping site (like Amazon Prime)
3. ``getCurrentDiscounts()``, which retrieves a list of all discounted products available now
4. ``isEligibleForDiscount(status, discounts)``, which determines if a user is eligible for any discounts
based on their membership status

To write the code to accomplish the above tasks, we can just call each function from top to bottom. 
Each time a function finishes, we forward its return value into the parameter of the next function 
that needs it. It is easy to write the code to do these tasks one by one.

However, if we want to reduce some time waiting on IO operations to complete, then we could instead execute
the functions concurrently. But, we can't just do all of them at once. For example, `isEligibleForDiscount`
depends on membership status and the available discounts, thus can only be run once everything else has been
completed. 

In this small example it is not too hard to figure out which functions can be called concurrently and which
need to wait for others to finish. However, in a larger codebase it can be extremely difficult to find the most
optimal scheduling. As a result, manually writing the code to chain together IO tasks is 
very error prone, hard to read, and often times suboptimal.

AcePy lets you do just the easy work, which is simply writing out the tasks one by one.
AcePy then analyzes your code to find the optimal ordering to execute every task.
**The result: write simple single threaded code but get all the performance benefits of multithreading for free!**
