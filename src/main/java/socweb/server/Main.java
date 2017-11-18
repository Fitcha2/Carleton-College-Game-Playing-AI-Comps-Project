/*
 * This file is part of the Java Settlers Web App.
 *
 * This file Copyright (C) 2017 Jeremy D Monin <jeremy@nand.net>
 *
 * Open-source license: TBD
 *
 * The maintainer of this program can be reached at https://github.com/jdmonin/jsettlers-webapp
 */

package socweb.server;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import javax.servlet.ServletContext;
import javax.servlet.ServletContextEvent;
import javax.servlet.ServletContextListener;

/**
 * Main class to run web app's SOCServer as a background thread.
 */
public class Main implements ServletContextListener
{
    /** Context attribute to find the server later */
    public static final String CONTEXT_ATTRIB_SERVER = "socweb.server";

    private ServletContext ctx;

    /**
     * Thread executor to start and run the server.
     */
    private ExecutorService srvRunner;

    private Runnable runner;  // Stand-in for SOCServer until ready

    public void contextInitialized(ServletContextEvent e)
    {
        srvRunner = Executors.newSingleThreadExecutor();
        runner = new Runner();
        ctx = e.getServletContext();
        ctx.log("Main: contextInitialized");
        ctx.setAttribute(CONTEXT_ATTRIB_SERVER, runner);
        srvRunner.submit(runner);
    }

    public void contextDestroyed(ServletContextEvent e)
    {
        e.getServletContext().setAttribute(CONTEXT_ATTRIB_SERVER, null);
        // TODO any server shutdown needed
        srvRunner.shutdownNow();  // TODO is .shutdown() too polite?
    }

    /** Main thread for SOCServer */
    public class Runner implements Runnable
    {
        public void run()
        {
            ctx.log("Runner starting.");

            boolean uninterrupted = true;
            while (uninterrupted)
            {
                ctx.log("Ping at " + System.currentTimeMillis());
                try
                {
                    Thread.sleep(10000);
                } catch (InterruptedException e) {
                    uninterrupted = false;
                }
            }

            ctx.log("Interrupted: Runner shutting down.");
        }
    }

    public static void main(String args[])
    {
        System.out.println
            ("This class launches SOCServer within its servlet container, and must be started from within a server like Jetty or Tomcat.");
        System.exit(1);
    }

}