"use client";

import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero Section */}
      <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 md:p-12 mb-8 text-center transition-colors">
        {/* Who We Are */}
        <div className="mb-10">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-800 dark:text-white mb-6">
            Our Fellow Travelers
          </h1>
          <div className="space-y-4 text-lg md:text-xl text-gray-700 dark:text-gray-300 leading-relaxed max-w-2xl mx-auto">
            <p>
              Our Fellow Travelers is an online AA group of Alcoholics Anonymous World Services.
            </p>
            <p>
              Our primary purpose is to stay sober and to help others recover from alcoholism.
            </p>
            <p>
              We welcome anyone who wishes to join us on a path of recovery.
            </p>
          </div>
        </div>

        {/* Meeting Details */}
        <div className="mb-10 pt-10 border-t border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl md:text-3xl font-bold text-slate-800 dark:text-white mb-6">
            Meeting Details
          </h2>
          <div className="space-y-6 text-left max-w-2xl mx-auto">
            <div className="bg-gray-50 dark:bg-gray-700 p-6 md:p-8 rounded-lg">
              <p className="text-xl md:text-2xl font-semibold text-slate-800 dark:text-white mb-6 text-center">
                Every day at 7:00 a.m. Central Time
              </p>
              
              <div className="space-y-5">
                <div>
                  <p className="font-semibold text-slate-800 dark:text-white mb-2">
                    Online with Video Option:
                  </p>
                  <p className="text-gray-700 dark:text-gray-300 mb-1 break-words">
                    <a 
                      href="https://join.freeconferencecall.com/timhwalton" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline"
                    >
                      https://join.freeconferencecall.com/timhwalton
                    </a>
                  </p>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">
                    Meeting ID: timhwalton
                  </p>
                </div>

                <div className="pt-2">
                  <p className="font-semibold text-slate-800 dark:text-white mb-2">
                    Phone Only:
                  </p>
                  <p className="text-gray-700 dark:text-gray-300">
                    <a 
                      href="tel:+19517999267" 
                      className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline text-lg"
                    >
                      (951) 799-9267
                    </a>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Donation Buttons */}
        <div className="pt-10 border-t border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl md:text-3xl font-bold text-slate-800 dark:text-white mb-4">
            7th Tradition
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-8">
            Support our group through the 7th Tradition
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button 
              asChild 
              size="lg"
              className="bg-[#3D95CE] hover:bg-[#2d7aa8] text-white px-10 py-6 text-lg font-semibold min-w-[160px]"
            >
              <a 
                href="https://venmo.com/your-username"
                target="_blank"
                rel="noopener noreferrer"
              >
                Venmo
              </a>
            </Button>
            <Button 
              asChild 
              size="lg"
              className="bg-[#0070BA] hover:bg-[#005a94] text-white px-10 py-6 text-lg font-semibold min-w-[160px]"
            >
              <a 
                href="https://www.paypal.com/donate/your-donation-link"
                target="_blank"
                rel="noopener noreferrer"
              >
                PayPal
              </a>
            </Button>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-6 italic">
            Replace URLs with your actual Venmo username and PayPal donation link
          </p>
        </div>
      </section>
    </div>
  );
}