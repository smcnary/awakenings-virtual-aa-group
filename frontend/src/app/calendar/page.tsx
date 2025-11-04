export default function Calendar() {
  return (
    <div>
        {/* Hero Section */}
        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 mb-8 text-center transition-colors">
          <h2 className="text-3xl font-bold text-slate-800 dark:text-white mb-4">Calendar</h2>
          <p className="text-lg text-gray-600 dark:text-gray-400">Upcoming events and special meetings</p>
        </section>

        {/* Content */}
        <div className="space-y-8">
          {/* Google Calendar Embed */}
          <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
            <h3 className="text-2xl font-bold text-slate-800 dark:text-white mb-4 border-b-2 border-blue-500 pb-2">Group Calendar</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">View our upcoming meetings and events</p>
            
            <div className="relative w-full" style={{ paddingBottom: '75%', height: 0, overflow: 'hidden' }}>
              <iframe
                src="https://calendar.google.com/calendar/embed?src=YOUR_CALENDAR_ID&ctz=America%2FChicago"
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%',
                  border: 0,
                }}
                title="Group Calendar"
                allowFullScreen
              />
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-4 italic">
              Replace YOUR_CALENDAR_ID with your Google Calendar ID. To get your calendar ID, go to Google Calendar settings → select your calendar → find the Calendar ID.
            </p>
          </section>

          <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
            <h3 className="text-2xl font-bold text-slate-800 dark:text-white mb-4 border-b-2 border-blue-500 pb-2">Regular Meeting Schedule</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">Our group meets daily at 7:00 a.m. Central Time</p>
            
            <div className="grid gap-4">
              <div className="bg-gray-50 dark:bg-gray-700 p-6 rounded-lg border-l-4 border-blue-500">
                <h4 className="text-xl font-semibold text-slate-800 dark:text-white mb-2">Monday - Saturday</h4>
                <p className="text-gray-600 dark:text-gray-400 mb-1">Online with video option and phone access</p>
                <p className="text-gray-600 dark:text-gray-400 mb-1"><strong>Time:</strong> 7:00 a.m. Central Time</p>
                <p className="text-gray-600 dark:text-gray-400"><strong>Platform:</strong> FreeConferenceCall.com</p>
              </div>
              
              <div className="bg-gray-50 dark:bg-gray-700 p-6 rounded-lg border-l-4 border-blue-500">
                <h4 className="text-xl font-semibold text-slate-800 dark:text-white mb-2">Sunday</h4>
                <p className="text-gray-600 dark:text-gray-400 mb-1">Phone and online only</p>
                <p className="text-gray-600 dark:text-gray-400 mb-1"><strong>Time:</strong> 7:00 a.m. Central Time</p>
                <p className="text-gray-600 dark:text-gray-400"><strong>Platform:</strong> FreeConferenceCall.com</p>
              </div>
            </div>
          </section>

          <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
            <h3 className="text-2xl font-bold text-slate-800 dark:text-white mb-4 border-b-2 border-blue-500 pb-2">Meeting Access Information</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">Join our meetings using the following information:</p>
            
            <div className="grid gap-4">
              <div className="bg-gray-50 dark:bg-gray-700 p-6 rounded-lg border-l-4 border-green-500">
                <h4 className="text-xl font-semibold text-slate-800 dark:text-white mb-2">Online Meeting</h4>
                <p className="text-gray-600 dark:text-gray-400 mb-1">
                  <strong>Link:</strong>{" "}
                  <a 
                    href="https://join.freeconferencecall.com/timhwalton" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                  >
                    https://join.freeconferencecall.com/timhwalton
                  </a>
                </p>
                <p className="text-gray-600 dark:text-gray-400"><strong>Meeting ID:</strong> timhwalton</p>
              </div>
              
              <div className="bg-gray-50 dark:bg-gray-700 p-6 rounded-lg border-l-4 border-green-500">
                <h4 className="text-xl font-semibold text-slate-800 dark:text-white mb-2">Phone Access</h4>
                <p className="text-gray-600 dark:text-gray-400 mb-1">
                  <strong>US Dial-in:</strong>{" "}
                  <a href="tel:+19517999267" className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300">
                    (951) 799-9267
                  </a>
                </p>
                <p className="text-gray-600 dark:text-gray-400">
                  <strong>International:</strong>{" "}
                  <a 
                    href="https://fccdl.in/i/timhwalton" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                  >
                    https://fccdl.in/i/timhwalton
                  </a>
                </p>
              </div>
            </div>
          </section>

          <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
            <h3 className="text-2xl font-bold text-slate-800 dark:text-white mb-4 border-b-2 border-blue-500 pb-2">Time Zone Information</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">Our meetings are held at 7:00 a.m. Central Time. Here's what that means for other time zones:</p>
            
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg text-center">
                <h4 className="text-lg font-semibold text-slate-800 dark:text-white mb-2">Eastern Time</h4>
                <p className="text-gray-600 dark:text-gray-400 font-semibold">8:00 a.m.</p>
              </div>
              
              <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg text-center">
                <h4 className="text-lg font-semibold text-slate-800 dark:text-white mb-2">Mountain Time</h4>
                <p className="text-gray-600 dark:text-gray-400 font-semibold">6:00 a.m.</p>
              </div>
              
              <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg text-center">
                <h4 className="text-lg font-semibold text-slate-800 dark:text-white mb-2">Pacific Time</h4>
                <p className="text-gray-600 dark:text-gray-400 font-semibold">5:00 a.m.</p>
              </div>
              
              <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg text-center">
                <h4 className="text-lg font-semibold text-slate-800 dark:text-white mb-2">Alaska Time</h4>
                <p className="text-gray-600 dark:text-gray-400 font-semibold">4:00 a.m.</p>
              </div>
              
              <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg text-center">
                <h4 className="text-lg font-semibold text-slate-800 dark:text-white mb-2">Hawaii Time</h4>
                <p className="text-gray-600 dark:text-gray-400 font-semibold">2:00 a.m.</p>
              </div>
            </div>
            
            <p className="text-gray-600 dark:text-gray-400 italic mt-6">Note: Times adjust for Daylight Saving Time changes.</p>
          </section>
        </div>
    </div>
  );
}
